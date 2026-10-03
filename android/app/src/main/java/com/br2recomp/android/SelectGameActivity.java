package com.br2recomp.android;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;

public class SelectGameActivity extends Activity {

    private static final String PREFS_NAME = "br2recomp_prefs";
    private static final String KEY_GAME_URI = "game_uri";
    private static final String KEY_BIOS_URI = "bios_uri";
    private static final int REQUEST_CODE_PICK_ISO = 1001;
    private static final int REQUEST_CODE_PICK_BIOS = 1002;

    private TextView statusText;
    private TextView biosStatusText;
    private Button launchButton;
    private Uri selectedUri;
    private Uri selectedBiosUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_select_game);

        statusText = findViewById(R.id.text_status);
        biosStatusText = findViewById(R.id.text_bios_status);
        launchButton = findViewById(R.id.button_launch);
        {
            android.content.SharedPreferences tcPrefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
            android.widget.CheckBox tcBoxInit = findViewById(R.id.check_touch);
            android.widget.SeekBar tcSeekInit = findViewById(R.id.seek_touch);
            if (tcBoxInit != null) tcBoxInit.setChecked(tcPrefs.getBoolean("touch_controls", true));
            if (tcSeekInit != null) tcSeekInit.setProgress(tcPrefs.getInt("touch_alpha", 20));
        }
        Button pickButton = findViewById(R.id.button_pick_iso);
        Button pickBiosButton = findViewById(R.id.button_pick_bios);

        pickButton.setOnClickListener(v -> openFilePicker());
        pickBiosButton.setOnClickListener(v -> openBiosPicker());
        launchButton.setOnClickListener(v -> launchGame());

        restoreSavedGame();
        restoreSavedBios();
        updateLaunchButtonState();
    }

    private void restoreSavedGame() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedUriString = prefs.getString(KEY_GAME_URI, null);
        if (savedUriString != null) {
            selectedUri = Uri.parse(savedUriString);
            statusText.setText("Disco guardado:\n" + selectedUri.getLastPathSegment());
        }
    }

    private void restoreSavedBios() {
        File biosFile = new File(new File(getFilesDir(), "bios"), "openbios.bin");
        if (biosFile.exists() && biosFile.length() > 0) {
            biosStatusText.setText("BIOS ya instalado (" + biosFile.length() + " bytes).");
            return;
        }
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedBiosUriString = prefs.getString(KEY_BIOS_URI, null);
        if (savedBiosUriString != null) {
            selectedBiosUri = Uri.parse(savedBiosUriString);
            biosStatusText.setText("BIOS seleccionado:\n" + selectedBiosUri.getLastPathSegment());
        }
    }

    private boolean isBiosAlreadyInstalled() {
        File biosFile = new File(new File(getFilesDir(), "bios"), "openbios.bin");
        return biosFile.exists() && biosFile.length() > 0;
    }

    private void updateLaunchButtonState() {
        boolean ready = selectedUri != null && (selectedBiosUri != null || isBiosAlreadyInstalled());
        launchButton.setEnabled(ready);
    }

    private void openFilePicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(intent, REQUEST_CODE_PICK_ISO);
    }

    private void openBiosPicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(intent, REQUEST_CODE_PICK_BIOS);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode != RESULT_OK || data == null) {
            return;
        }
        Uri uri = data.getData();
        if (uri == null) {
            return;
        }
        getContentResolver().takePersistableUriPermission(
                uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);

        if (requestCode == REQUEST_CODE_PICK_ISO) {
            selectedUri = uri;
            getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                    .edit()
                    .putString(KEY_GAME_URI, uri.toString())
                    .apply();

            statusText.setText("Disco seleccionado:\n" + uri.getLastPathSegment());
            Toast.makeText(this, "Disco guardado correctamente", Toast.LENGTH_SHORT).show();
            updateLaunchButtonState();
        } else if (requestCode == REQUEST_CODE_PICK_BIOS) {
            selectedBiosUri = uri;
            getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                    .edit()
                    .putString(KEY_BIOS_URI, uri.toString())
                    .apply();

            biosStatusText.setText("BIOS seleccionado:\n" + uri.getLastPathSegment());
            Toast.makeText(this, "BIOS guardado correctamente", Toast.LENGTH_SHORT).show();
            updateLaunchButtonState();
        }
    }

    private void launchGame() {
        if (selectedUri == null) {
            Toast.makeText(this, "Primero selecciona el disco del juego", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(this, MainActivity.class);
        intent.putExtra("GAME_URI", selectedUri.toString());
        if (selectedBiosUri != null) {
            intent.putExtra("BIOS_URI", selectedBiosUri.toString());
        }
        {
            android.widget.CheckBox tcBox = findViewById(R.id.check_touch);
            android.widget.SeekBar tcSeek = findViewById(R.id.seek_touch);
            boolean tcOn = tcBox == null || tcBox.isChecked();
            int tcProg = tcSeek != null ? tcSeek.getProgress() : 20;
            getSharedPreferences(PREFS_NAME, MODE_PRIVATE).edit().putBoolean("touch_controls", tcOn).putInt("touch_alpha", tcProg).apply();
            intent.putExtra("TOUCH_CONTROLS", tcOn);
            intent.putExtra("TOUCH_ALPHA", 20 + tcProg);
        }
        startActivity(intent);
    }
}
