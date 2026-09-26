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

/**
 * Pantalla inicial (LAUNCHER). Antes de arrancar el runtime nativo
 * (MainActivity/SDLActivity), el usuario debe elegir el archivo del disco
 * del juego (.bin/.cue/.iso/.chd) y, la primera vez, el BIOS de PlayStation
 * (SCPH1001.BIN, 512 KB) desde el propio almacenamiento del celular, usando
 * el selector de archivos del sistema (Storage Access Framework) — así no
 * necesitamos permisos amplios de almacenamiento.
 *
 * Las rutas elegidas se guardan en SharedPreferences como "content:// URI"
 * con permiso persistente, para no tener que volver a pedirlas cada vez.
 * El BIOS además se copia a almacenamiento privado (files/bios/SCPH1001.BIN)
 * en MainActivity, así que una vez copiado no hace falta volver a
 * seleccionarlo en corridas futuras.
 */
public class SelectGameActivity extends Activity {

    private static final String PREFS_NAME = "br2recomp_prefs";
    private static final String KEY_GAME_URI = "game_uri";
    private static final String KEY_BIOS_URI = "bios_uri";
    private static final int REQUEST_CODE_PICK_ISO = 1001;
    private static final int REQUEST_CODE_PICK_BIOS = 1002;
    private static final long EXPECTED_BIOS_SIZE = 524288L; // 512 KB

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
        // Si el BIOS ya fue copiado a almacenamiento privado en una corrida
        // anterior, no hace falta volver a seleccionarlo.
        File biosFile = new File(new File(getFilesDir(), "bios"), "SCPH1001.BIN");
        if (biosFile.exists() && biosFile.length() == EXPECTED_BIOS_SIZE) {
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
        File biosFile = new File(new File(getFilesDir(), "bios"), "SCPH1001.BIN");
        return biosFile.exists() && biosFile.length() == EXPECTED_BIOS_SIZE;
    }

    private void updateLaunchButtonState() {
        boolean ready = selectedUri != null && (selectedBiosUri != null || isBiosAlreadyInstalled());
        launchButton.setEnabled(ready);
    }

    private void openFilePicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        // "*/*" porque .bin/.cue/.chd no siempre tienen un MIME type
        // reconocido por Android; filtramos por extensión al recibir el
        // resultado en su lugar.
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
        // Permiso persistente para poder leer este archivo en próximos
        // arranques de la app sin volver a pedirlo.
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
        startActivity(intent);
    }
}
