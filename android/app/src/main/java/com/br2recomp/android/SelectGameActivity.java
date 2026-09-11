package com.br2recomp.android;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Pantalla inicial (LAUNCHER). Antes de arrancar el runtime nativo
 * (MainActivity/SDLActivity), el usuario debe elegir el archivo del disco
 * del juego (.bin/.cue/.iso/.chd) desde el propio almacenamiento del
 * celular, usando el selector de archivos del sistema (Storage Access
 * Framework) — así no necesitamos permisos amplios de almacenamiento.
 *
 * La ruta elegida se guarda en SharedPreferences como un "content:// URI"
 * con permiso persistente, para no tener que volver a pedirla cada vez que
 * se abre la app.
 *
 * NOTA: esta activity solo resuelve el URI y lo guarda/pasa. La lectura
 * real de ese disco desde el runtime C/C++ de psxrecomp todavía es un paso
 * pendiente de conectar (ver el TODO en android_main_glue.c) — un
 * content:// URI no es una ruta de archivo normal, así que probablemente
 * haya que copiar el contenido a un archivo temporal legible por el
 * código nativo, o abrir el file descriptor con
 * getContentResolver().openFileDescriptor(uri, "r") y pasar ese descriptor
 * al C++ vía JNI en lugar de una ruta de texto.
 */
public class SelectGameActivity extends Activity {

    private static final String PREFS_NAME = "br2recomp_prefs";
    private static final String KEY_GAME_URI = "game_uri";
    private static final int REQUEST_CODE_PICK_ISO = 1001;

    private TextView statusText;
    private Button launchButton;
    private Uri selectedUri;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_select_game);

        statusText = findViewById(R.id.text_status);
        launchButton = findViewById(R.id.button_launch);
        Button pickButton = findViewById(R.id.button_pick_iso);

        pickButton.setOnClickListener(v -> openFilePicker());
        launchButton.setOnClickListener(v -> launchGame());

        restoreSavedGame();
    }

    private void restoreSavedGame() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedUriString = prefs.getString(KEY_GAME_URI, null);
        if (savedUriString != null) {
            selectedUri = Uri.parse(savedUriString);
            statusText.setText("Disco guardado:\n" + selectedUri.getLastPathSegment());
            launchButton.setEnabled(true);
        }
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

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE_PICK_ISO && resultCode == RESULT_OK && data != null) {
            Uri uri = data.getData();
            if (uri == null) {
                return;
            }
            // Permiso persistente para poder leer este archivo en próximos
            // arranques de la app sin volver a pedirlo.
            getContentResolver().takePersistableUriPermission(
                    uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);

            selectedUri = uri;
            getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
                    .edit()
                    .putString(KEY_GAME_URI, uri.toString())
                    .apply();

            statusText.setText("Disco seleccionado:\n" + uri.getLastPathSegment());
            launchButton.setEnabled(true);
            Toast.makeText(this, "Disco guardado correctamente", Toast.LENGTH_SHORT).show();
        }
    }

    private void launchGame() {
        if (selectedUri == null) {
            Toast.makeText(this, "Primero selecciona el disco del juego", Toast.LENGTH_SHORT).show();
            return;
        }
        Intent intent = new Intent(this, MainActivity.class);
        intent.putExtra("GAME_URI", selectedUri.toString());
        startActivity(intent);
    }
}
