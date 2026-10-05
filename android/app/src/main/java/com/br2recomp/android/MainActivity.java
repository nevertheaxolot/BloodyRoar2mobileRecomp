package com.br2recomp.android;

import android.database.Cursor;
import android.net.Uri;
import android.provider.OpenableColumns;
import android.util.Log;

import org.libsdl.app.SDLActivity;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.ArrayList;

public class MainActivity extends SDLActivity {

    private static final String TAG = "BR2Recomp";

    private String gameUriString;
    private String biosUriString;

    @Override
    protected void onCreate(android.os.Bundle savedInstanceState) {
        gameUriString = getIntent().getStringExtra("GAME_URI");
        biosUriString = getIntent().getStringExtra("BIOS_URI");
        try {
            android.system.Os.setenv("PSX_EXE_DIR_OVERRIDE", getFilesDir().getAbsolutePath(), true);
        } catch (Exception e) {
            Log.e(TAG, "onCreate: no se pudo setear PSX_EXE_DIR_OVERRIDE", e);
        }
        if (biosUriString != null) {
            try {
                Uri biosUri = Uri.parse(biosUriString);
                File biosDir = new File(getFilesDir(), "bios");
                if (!biosDir.exists()) {
                    biosDir.mkdirs();
                }
                File biosOut = new File(biosDir, "openbios.bin");
                copyUriToFile(biosUri, biosOut);
                Log.i(TAG, "onCreate: BIOS copiado a " + biosOut.getAbsolutePath() + " (" + biosOut.length() + " bytes)");
            } catch (Exception e) {
                Log.e(TAG, "onCreate: excepcion copiando el BIOS", e);
            }
        }
        br2PrepareInput();
        super.onCreate(savedInstanceState);
        br2AddTouchOverlay();
        br2ImmersiveFlags();
    }

    @Override
    protected String[] getLibraries() {
        return new String[]{
                "SDL2",
                "psx_android"
        };
    }

    @Override
    protected String[] getArguments() {
        if (gameUriString == null) {
            Log.w(TAG, "getArguments: no se recibio GAME_URI, arrancando sin --disc");
            return new String[]{};
        }
        try {
            Uri uri = Uri.parse(gameUriString);
            File localDisc = resolveDiscToLocalFile(uri);
            if (localDisc == null) {
                Log.e(TAG, "getArguments: no se pudo resolver el disco a un archivo local");
                return new String[]{};
            }

            ArrayList<String> argList = new ArrayList<>();
            argList.add(getFilesDir().getAbsolutePath() + "/psxrecomp");
            argList.add("--disc");
            argList.add(localDisc.getAbsolutePath());

            File biosFile = new File(new File(getFilesDir(), "bios"), "openbios.bin");
            if (biosFile.exists()) {
                argList.add("--bios");
                argList.add(biosFile.getAbsolutePath());
            } else {
                Log.w(TAG, "getArguments: no se encontro BIOS en " + biosFile.getAbsolutePath());
            }

            argList.add("--no-launcher");

            String[] args = argList.toArray(new String[0]);
            Log.i(TAG, "getArguments: array completo = " + java.util.Arrays.toString(args));
            return args;
        } catch (Exception e) {
            Log.e(TAG, "getArguments: excepcion resolviendo el disco", e);
            return new String[]{};
        }
    }

    private File resolveDiscToLocalFile(Uri uri) throws Exception {
        String displayName = queryDisplayName(uri);
        if (displayName == null || displayName.isEmpty()) {
            displayName = "disc.bin";
        }
        File outFile = new File(getFilesDir(), displayName);

        long expectedSize = querySize(uri);
        if (outFile.exists() && expectedSize > 0 && outFile.length() == expectedSize) {
            Log.i(TAG, "resolveDiscToLocalFile: usando copia en cache (" + outFile.length() + " bytes)");
            return outFile;
        }

        copyUriToFile(uri, outFile);
        return outFile;
    }

    private void copyUriToFile(Uri uri, File outFile) throws Exception {
        Log.i(TAG, "copyUriToFile: copiando a " + outFile.getAbsolutePath());
        try (InputStream in = getContentResolver().openInputStream(uri);
             OutputStream out = new FileOutputStream(outFile)) {
            if (in == null) {
                throw new Exception("openInputStream devolvio null para " + uri);
            }
            byte[] buffer = new byte[1024 * 1024];
            int read;
            while ((read = in.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
        }
        Log.i(TAG, "copyUriToFile: copia terminada (" + outFile.length() + " bytes)");
    }

    private String queryDisplayName(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int idx = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (idx >= 0) {
                    return cursor.getString(idx);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "queryDisplayName fallo", e);
        }
        return null;
    }

    private long querySize(Uri uri) {
        try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
            if (cursor != null && cursor.moveToFirst()) {
                int idx = cursor.getColumnIndex(OpenableColumns.SIZE);
                if (idx >= 0 && !cursor.isNull(idx)) {
                    return cursor.getLong(idx);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "querySize fallo", e);
        }
        return -1;
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        android.os.Process.killProcess(android.os.Process.myPid());
    }

    private boolean br2TouchOn = true;
    private boolean br2UseOverlay = false;
    private int br2TouchAlpha = 40;

    private boolean br2HasGamepad() {
        try {
            for (int id : android.view.InputDevice.getDeviceIds()) {
                android.view.InputDevice d = android.view.InputDevice.getDevice(id);
                if (d == null || d.isVirtual()) continue;
                int src = d.getSources();
                if ((src & android.view.InputDevice.SOURCE_GAMEPAD) == android.view.InputDevice.SOURCE_GAMEPAD
                        || (src & android.view.InputDevice.SOURCE_JOYSTICK) == android.view.InputDevice.SOURCE_JOYSTICK) {
                    return true;
                }
            }
        } catch (Throwable t) {
            Log.e("BR2Input", "deteccion de mando fallo", t);
        }
        return false;
    }

    private void br2ApplyEnv() {
        String t = getIntent().getStringExtra("ENV_TEXT");
        if (t == null) return;
        for (String line : t.split("\\r?\\n")) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            int eq = line.indexOf('=');
            if (eq <= 0) continue;
            String k = line.substring(0, eq).trim();
            String v = line.substring(eq + 1).trim();
            if (!k.matches("(PSX|BR2)_[A-Z0-9_]+") || v.length() > 200) {
                Log.w("BR2Input", "env ignorada: " + line);
                continue;
            }
            try {
                android.system.Os.setenv(k, v, true);
                Log.i("BR2Input", "env " + k + "=" + v);
            } catch (Throwable e) {
                Log.e("BR2Input", "setenv fallo: " + k, e);
            }
        }
    }

    private void br2PrepareInput() {
        br2TouchOn = getIntent().getBooleanExtra("TOUCH_CONTROLS", true);
        br2TouchAlpha = getIntent().getIntExtra("TOUCH_ALPHA", 40);
        boolean pad = br2HasGamepad();
        br2UseOverlay = br2TouchOn && !pad;
        try {
            android.system.Os.setenv("BR2_P1_DEVICE", pad ? "gamepad" : "keyboard", true);
        } catch (Throwable t) {
            Log.e("BR2Input", "setenv BR2_P1_DEVICE fallo", t);
        }
        Log.i("BR2Input", "pad=" + pad + " touch=" + br2TouchOn + " overlay=" + br2UseOverlay + " alpha=" + br2TouchAlpha);
        br2ApplyEnv();
    }

    private void br2AddTouchOverlay() {
        if (!br2UseOverlay) return;
        try {
            TouchControlsView v = new TouchControlsView(this);
            v.setAlphaPercent(br2TouchAlpha);
            addContentView(v, new android.view.ViewGroup.LayoutParams(
                    android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                    android.view.ViewGroup.LayoutParams.MATCH_PARENT));
        } catch (Throwable t) {
            Log.e("BR2Input", "overlay tactil fallo", t);
        }
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) br2ImmersiveFlags();
    }

    private void br2ImmersiveFlags() {
        try {
            getWindow().getDecorView().setSystemUiVisibility(
                    android.view.View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | android.view.View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | android.view.View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | android.view.View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | android.view.View.SYSTEM_UI_FLAG_FULLSCREEN
                    | android.view.View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        } catch (Throwable t) {
            Log.e("BR2Input", "modo inmersivo fallo", t);
        }
    }
}
