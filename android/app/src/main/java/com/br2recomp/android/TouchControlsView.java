package com.br2recomp.android;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RadialGradient;
import android.graphics.Shader;
import android.graphics.Typeface;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;

import org.libsdl.app.SDLActivity;

import java.util.HashSet;
import java.util.Set;

/** Controles tactiles: resplandor rojo + simbolos amarillos. Cada boton genera la tecla por defecto del juego. */
public class TouchControlsView extends View {
    private static final int K_UP = KeyEvent.KEYCODE_DPAD_UP;
    private static final int K_DOWN = KeyEvent.KEYCODE_DPAD_DOWN;
    private static final int K_LEFT = KeyEvent.KEYCODE_DPAD_LEFT;
    private static final int K_RIGHT = KeyEvent.KEYCODE_DPAD_RIGHT;
    private static final int K_CROSS = KeyEvent.KEYCODE_X;
    private static final int K_CIRCLE = KeyEvent.KEYCODE_S;
    private static final int K_SQUARE = KeyEvent.KEYCODE_Z;
    private static final int K_TRIANGLE = KeyEvent.KEYCODE_A;
    private static final int K_L1 = KeyEvent.KEYCODE_Q;
    private static final int K_R1 = KeyEvent.KEYCODE_W;
    private static final int K_L2 = KeyEvent.KEYCODE_E;
    private static final int K_R2 = KeyEvent.KEYCODE_R;
    private static final int K_START = KeyEvent.KEYCODE_ENTER;
    private static final int K_SELECT = KeyEvent.KEYCODE_SHIFT_RIGHT;

    private final Set<Integer> down = new HashSet<>();
    private final Paint glow = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint ink = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint label = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path path = new Path();
    private final Shader glowShader = new RadialGradient(0f, 0f, 1f,
            new int[]{0xFFFF1A1A, 0xCCFF0000, 0x00FF0000},
            new float[]{0f, 0.45f, 1f}, Shader.TileMode.CLAMP);
    private int alpha = 140;

    private float dpCx, dpCy, dpR;
    private float fbCx, fbCy, fbOff, fbR;
    private float shR, sh2R, ssR;
    private float l1x, l1y, r1x, r1y, l2x, l2y, r2x, r2y, slx, sly, stx, sty;

    public TouchControlsView(Context context) {
        super(context);
        glow.setShader(glowShader);
        glow.setStyle(Paint.Style.FILL);
        ink.setStyle(Paint.Style.STROKE);
        ink.setStrokeCap(Paint.Cap.ROUND);
        ink.setStrokeJoin(Paint.Join.ROUND);
        label.setTextAlign(Paint.Align.CENTER);
        label.setTypeface(Typeface.create(Typeface.SANS_SERIF, Typeface.BOLD_ITALIC));
        setFocusable(false);
    }

    public void setAlphaPercent(int pct) {
        if (pct < 10) pct = 10;
        if (pct > 100) pct = 100;
        alpha = pct * 255 / 100;
        invalidate();
    }

    @Override
    protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        super.onSizeChanged(w, h, oldw, oldh);
        ink.setStrokeWidth(Math.max(3f, 0.016f * h));
        dpR = 0.21f * h;
        dpCx = 0.097f * w;
        dpCy = 0.54f * h;
        fbR = 0.095f * h;
        fbOff = 0.215f * h;
        fbCx = 0.863f * w;
        fbCy = 0.55f * h;
        shR = 0.085f * h;
        sh2R = 0.06f * h;
        ssR = 0.065f * h;
        l1x = 0.16f * w; l1y = 0.075f * h;
        r1x = 0.80f * w; r1y = 0.075f * h;
        l2x = 0.06f * w; l2y = 0.075f * h;
        r2x = 0.93f * w; r2y = 0.075f * h;
        slx = 0.225f * w; sly = 0.88f * h;
        stx = 0.72f * w; sty = 0.88f * h;
    }

    private boolean near(float x, float y, float cx, float cy, float r) {
        return Math.hypot(x - cx, y - cy) <= r * 1.25f;
    }

    private void collect(float x, float y, Set<Integer> out) {
        float dx = x - dpCx, dy = y - dpCy;
        if (Math.hypot(dx, dy) <= dpR * 1.4f) {
            float dz = dpR * 0.28f;
            if (dx < -dz) out.add(K_LEFT);
            if (dx > dz) out.add(K_RIGHT);
            if (dy < -dz) out.add(K_UP);
            if (dy > dz) out.add(K_DOWN);
        }
        if (near(x, y, fbCx, fbCy - fbOff, fbR)) out.add(K_TRIANGLE);
        if (near(x, y, fbCx + fbOff, fbCy, fbR)) out.add(K_CIRCLE);
        if (near(x, y, fbCx, fbCy + fbOff, fbR)) out.add(K_CROSS);
        if (near(x, y, fbCx - fbOff, fbCy, fbR)) out.add(K_SQUARE);
        if (near(x, y, l1x, l1y, shR)) out.add(K_L1);
        if (near(x, y, r1x, r1y, shR)) out.add(K_R1);
        if (near(x, y, l2x, l2y, sh2R)) out.add(K_L2);
        if (near(x, y, r2x, r2y, sh2R)) out.add(K_R2);
        if (near(x, y, slx, sly, ssR)) out.add(K_SELECT);
        if (near(x, y, stx, sty, ssR)) out.add(K_START);
    }

    @Override
    public boolean onTouchEvent(MotionEvent e) {
        int action = e.getActionMasked();
        int skip = -1;
        if (action == MotionEvent.ACTION_POINTER_UP || action == MotionEvent.ACTION_UP) {
            skip = e.getActionIndex();
        }
        Set<Integer> now = new HashSet<>();
        if (action != MotionEvent.ACTION_CANCEL) {
            for (int i = 0; i < e.getPointerCount(); i++) {
                if (i == skip) continue;
                collect(e.getX(i), e.getY(i), now);
            }
        }
        boolean changed = false;
        for (int k : now) {
            if (!down.contains(k)) { SDLActivity.onNativeKeyDown(k); changed = true; }
        }
        for (int k : down) {
            if (!now.contains(k)) { SDLActivity.onNativeKeyUp(k); changed = true; }
        }
        if (changed) {
            down.clear();
            down.addAll(now);
            invalidate();
        }
        return true;
    }

    private void releaseAll() {
        for (int k : down) SDLActivity.onNativeKeyUp(k);
        down.clear();
        invalidate();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (!hasFocus) releaseAll();
    }

    @Override
    protected void onDetachedFromWindow() {
        releaseAll();
        super.onDetachedFromWindow();
    }

    private void drawGlow(Canvas c, float cx, float cy, float r, boolean on) {
        glow.setAlpha(on ? Math.min(255, alpha + 110) : alpha);
        c.save();
        c.translate(cx, cy);
        c.scale(r, r);
        c.drawCircle(0f, 0f, 1f, glow);
        c.restore();
    }

    private void inkStyle(boolean on) {
        ink.setColor(on ? 0xFFFFFFA0 : 0xFFFFE600);
        ink.setAlpha(Math.min(255, alpha + (on ? 115 : 80)));
    }

    private void arrow(Canvas c, float dx, float dy, boolean on) {
        if (on) drawGlow(c, dpCx + dx * dpR * 0.6f, dpCy + dy * dpR * 0.6f, dpR * 0.55f, true);
        inkStyle(on);
        float bx = dpCx + dx * dpR * 0.22f, by = dpCy + dy * dpR * 0.22f;
        float tx = dpCx + dx * dpR * 0.95f, ty = dpCy + dy * dpR * 0.95f;
        float px = -dy, py = dx;
        float hl = dpR * 0.30f, hw = dpR * 0.26f;
        c.drawLine(bx, by, tx, ty, ink);
        c.drawLine(tx, ty, tx - dx * hl + px * hw, ty - dy * hl + py * hw, ink);
        c.drawLine(tx, ty, tx - dx * hl - px * hw, ty - dy * hl - py * hw, ink);
    }

    private void face(Canvas c, float cx, float cy, int kind, boolean on) {
        drawGlow(c, cx, cy, fbR * 1.25f, on);
        inkStyle(on);
        float s = fbR * 0.55f;
        switch (kind) {
            case 0:
                path.reset();
                path.moveTo(cx, cy - s);
                path.lineTo(cx + s, cy + s * 0.8f);
                path.lineTo(cx - s, cy + s * 0.8f);
                path.close();
                c.drawPath(path, ink);
                break;
            case 1:
                c.drawCircle(cx, cy, s, ink);
                break;
            case 2:
                c.drawLine(cx - s, cy - s, cx + s, cy + s, ink);
                c.drawLine(cx - s, cy + s, cx + s, cy - s, ink);
                break;
            default:
                c.drawRect(cx - s, cy - s, cx + s, cy + s, ink);
        }
    }

    private void pill(Canvas c, float cx, float cy, float r, String t, boolean on) {
        drawGlow(c, cx, cy, r * 1.3f, on);
        label.setColor(on ? 0xFFFFFFA0 : 0xFFFFE600);
        label.setAlpha(Math.min(255, alpha + (on ? 115 : 80)));
        label.setTextSize(r * (t.length() > 1 ? 0.9f : 1.25f));
        c.drawText(t, cx, cy - (label.ascent() + label.descent()) / 2f, label);
    }

    @Override
    protected void onDraw(Canvas c) {
        drawGlow(c, dpCx, dpCy, dpR * 0.9f, false);
        arrow(c, 0f, -1f, down.contains(K_UP));
        arrow(c, 0f, 1f, down.contains(K_DOWN));
        arrow(c, -1f, 0f, down.contains(K_LEFT));
        arrow(c, 1f, 0f, down.contains(K_RIGHT));
        face(c, fbCx, fbCy - fbOff, 0, down.contains(K_TRIANGLE));
        face(c, fbCx + fbOff, fbCy, 1, down.contains(K_CIRCLE));
        face(c, fbCx, fbCy + fbOff, 2, down.contains(K_CROSS));
        face(c, fbCx - fbOff, fbCy, 3, down.contains(K_SQUARE));
        pill(c, l1x, l1y, shR, "L", down.contains(K_L1));
        pill(c, r1x, r1y, shR, "R", down.contains(K_R1));
        pill(c, l2x, l2y, sh2R, "L2", down.contains(K_L2));
        pill(c, r2x, r2y, sh2R, "R2", down.contains(K_R2));
        pill(c, slx, sly, ssR, "SL", down.contains(K_SELECT));
        pill(c, stx, sty, ssR, "ST", down.contains(K_START));
    }
}
