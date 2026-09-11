package com.br2recomp.android;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.PointF;
import android.util.AttributeSet;
import android.view.MotionEvent;
import android.view.View;

import org.libsdl.app.SDLActivity;

import java.util.HashMap;
import java.util.Map;

/**
 * Overlay táctil simple: un joystick virtual (movimiento) a la izquierda y
 * 4 botones de acción a la derecha (equivalentes a los botones de forma de
 * un DualShock: cuadrado/triángulo/círculo/equis, que en Bloody Roar 2
 * corresponden a golpe/patada/transformación/agarre).
 *
 * Este overlay va DENTRO de la misma Activity que SDLSurface, superpuesto
 * (por ejemplo en un FrameLayout). No sustituye el input real: traduce cada
 * toque en un evento sintético que SDL2 ya sabe interpretar como si viniera
 * de un joystick/gamepad conectado, usando la API pública de SDLActivity.
 *
 * NOTA: los nombres de botones (BUTTON_SQUARE, etc.) y el mapeo final deben
 * ajustarse a como el runtime de psxrecomp lea el input del pad — revisa
 * cómo psxrecomp traduce eventos de SDL_GameController a los botones del
 * PSX original antes de fijar el mapeo definitivo.
 */
public class TouchControlsView extends View {

    private static final float STICK_RADIUS = 140f;
    private static final float BUTTON_RADIUS = 80f;

    private final PointF stickCenter = new PointF();
    private final PointF stickTouch = new PointF();
    private boolean stickActive = false;
    private int stickPointerId = -1;

    // Botones de acción: id -> centro
    private final Map<Integer, PointF> actionButtons = new HashMap<>();
    private final Map<Integer, Integer> activeButtonPointers = new HashMap<>();

    private final Paint bgPaint = new Paint();
    private final Paint fgPaint = new Paint();

    public TouchControlsView(Context context, AttributeSet attrs) {
        super(context, attrs);
        bgPaint.setColor(Color.argb(90, 255, 255, 255));
        fgPaint.setColor(Color.argb(160, 255, 255, 255));
        setWillNotDraw(false);
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        // Joystick abajo-izquierda
        stickCenter.set(220f, h - 220f);
        stickTouch.set(stickCenter.x, stickCenter.y);

        // 4 botones en rombo abajo-derecha (imitando la disposición de un pad)
        float bx = w - 260f;
        float by = h - 260f;
        actionButtons.put(0, new PointF(bx, by - 90f));       // arriba
        actionButtons.put(1, new PointF(bx + 90f, by));       // derecha
        actionButtons.put(2, new PointF(bx, by + 90f));       // abajo
        actionButtons.put(3, new PointF(bx - 90f, by));       // izquierda
    }

    @Override
    protected void onDraw(Canvas canvas) {
        canvas.drawCircle(stickCenter.x, stickCenter.y, STICK_RADIUS, bgPaint);
        canvas.drawCircle(stickTouch.x, stickTouch.y, 60f, fgPaint);

        for (Map.Entry<Integer, PointF> e : actionButtons.entrySet()) {
            PointF p = e.getValue();
            boolean pressed = activeButtonPointers.containsKey(e.getKey());
            canvas.drawCircle(p.x, p.y, BUTTON_RADIUS,
                    pressed ? fgPaint : bgPaint);
        }
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        int action = event.getActionMasked();
        int index = event.getActionIndex();
        int pointerId = event.getPointerId(index);
        float x = event.getX(index);
        float y = event.getY(index);

        switch (action) {
            case MotionEvent.ACTION_DOWN:
            case MotionEvent.ACTION_POINTER_DOWN:
                handleDown(pointerId, x, y);
                break;
            case MotionEvent.ACTION_MOVE:
                for (int i = 0; i < event.getPointerCount(); i++) {
                    handleMove(event.getPointerId(i), event.getX(i), event.getY(i));
                }
                break;
            case MotionEvent.ACTION_UP:
            case MotionEvent.ACTION_POINTER_UP:
            case MotionEvent.ACTION_CANCEL:
                handleUp(pointerId);
                break;
        }
        invalidate();
        return true;
    }

    private boolean within(float x, float y, PointF center, float radius) {
        float dx = x - center.x;
        float dy = y - center.y;
        return (dx * dx + dy * dy) <= radius * radius * 4; // margen táctil generoso
    }

    private void handleDown(int pointerId, float x, float y) {
        if (!stickActive && within(x, y, stickCenter, STICK_RADIUS)) {
            stickActive = true;
            stickPointerId = pointerId;
            updateStick(x, y);
            return;
        }
        for (Map.Entry<Integer, PointF> e : actionButtons.entrySet()) {
            if (within(x, y, e.getValue(), BUTTON_RADIUS)
                    && !activeButtonPointers.containsKey(e.getKey())) {
                activeButtonPointers.put(e.getKey(), pointerId);
                sendButton(e.getKey(), true);
            }
        }
    }

    private void handleMove(int pointerId, float x, float y) {
        if (stickActive && pointerId == stickPointerId) {
            updateStick(x, y);
        }
    }

    private void handleUp(int pointerId) {
        if (pointerId == stickPointerId) {
            stickActive = false;
            stickPointerId = -1;
            stickTouch.set(stickCenter.x, stickCenter.y);
            sendAxis(0, 0);
        }
        Integer releasedButton = null;
        for (Map.Entry<Integer, Integer> e : activeButtonPointers.entrySet()) {
            if (e.getValue() == pointerId) {
                releasedButton = e.getKey();
                break;
            }
        }
        if (releasedButton != null) {
            activeButtonPointers.remove(releasedButton);
            sendButton(releasedButton, false);
        }
    }

    private void updateStick(float x, float y) {
        float dx = x - stickCenter.x;
        float dy = y - stickCenter.y;
        float dist = (float) Math.sqrt(dx * dx + dy * dy);
        float maxDist = STICK_RADIUS;
        if (dist > maxDist) {
            dx = dx / dist * maxDist;
            dy = dy / dist * maxDist;
        }
        stickTouch.set(stickCenter.x + dx, stickCenter.y + dy);
        sendAxis(dx / maxDist, dy / maxDist);
    }

    /**
     * Envía el estado del stick como si fuera un joystick/gamepad conectado.
     * SDLActivity expone un canal para inyectar eventos de "joystick virtual"
     * mediante su clase SDLControllerManager; el detalle exacto de la llamada
     * depende de la versión de SDL2-Android que integres (revisa
     * SDLActivity.onNativePadDown / onNativeJoy en la fuente de SDL2 que
     * descargues, y ajusta estas llamadas para que coincidan).
     */
    private void sendAxis(float x, float y) {
        // TODO: reemplazar por la llamada real, p. ej.:
        // SDLActivity.onNativeJoy(0, 0, x);
        // SDLActivity.onNativeJoy(0, 1, y);
    }

    private void sendButton(int buttonId, boolean pressed) {
        // TODO: reemplazar por la llamada real, p. ej.:
        // SDLActivity.onNativePadButton(0, buttonId, pressed ? 1 : 0);
    }
}
