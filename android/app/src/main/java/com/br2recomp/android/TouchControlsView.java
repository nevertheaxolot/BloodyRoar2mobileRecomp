package com.br2recomp.android;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.Path;
import android.graphics.RectF;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;

import org.libsdl.app.SDLActivity;

import java.util.HashSet;
import java.util.Set;

/** Controles tactiles: cada boton genera la tecla que el juego ya tiene por defecto. */
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
    private final Paint fill = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint stroke = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Paint text = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final Path path = new Path();
    private final RectF tmp = new RectF();
    private int alpha = 100;

    private float dpCx, dpCy, dpR;
    private float fbCx, fbCy, fbOff, fbR;
    private final RectF rL1 = new RectF();
    private final RectF rL2 = new RectF();
    private final RectF rR1 = new RectF();
    private final RectF rR2 = new RectF();
    private final RectF rStart = new RectF();
    private final RectF rSelect = new RectF();

    public TouchControlsView(Context context) {
        super(context);
        stroke.setStyle(Paint.Style.STROKE);
        text.setTextAlign(Paint.Align.CENTER);
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
        dpR = 0.17f * h;
        dpCx = 0.113f * w;
        dpCy = 0.66f * h;
        fbR = 0.075f * h;
        fbOff = 0.125f * h;
        fbCx = 0.887f * w;
        fbCy = 0.66f * h;
        float bw = 0.17f * w, bh = 0.095f * h, gap = 0.02f * h, top = 0.06f * h;
        float lx = 0.028f * w, rx = w - 0.028f * w - bw;
        rL2.set(lx, top, lx + bw, top + bh);
        rL1.set(lx, top + bh + gap, lx + bw, top + 2 * bh + gap);
        rR2.set(rx, top, rx + bw, top + bh);
        rR1.set(rx, top + bh + gap, rx + bw, top + 2 * bh + gap);
        float sw = 0.12f * w, sh = 0.07f * h, sy = 0.90f * h;
        rSelect.set(0.06f * w, sy - sh / 2, 0.06f * w + sw, sy + sh / 2);
        rStart.set(w - 0.06f * w - sw, sy - sh / 2, w - 0.06f * w, sy + sh / 2);
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
        float lim = fbR * 1.15f;
        if (Math.hypot(x - fbCx, y - (fbCy - fbOff)) <= lim) out.add(K_TRIANGLE);
        if (Math.hypot(x - (fbCx + fbOff), y - fbCy) <= lim) out.add(K_CIRCLE);
        if (Math.hypot(x - fbCx, y - (fbCy + fbOff)) <= lim) out.add(K_CROSS);
        if (Math.hypot(x - (fbCx - fbOff), y - fbCy) <= lim) out.add(K_SQUARE);
        if (hit(rL1, x, y)) out.add(K_L1);
        if (hit(rL2, x, y)) out.add(K_L2);
        if (hit(rR1, x, y)) out.add(K_R1);
        if (hit(rR2, x, y)) out.add(K_R2);
        if (hit(rStart, x, y)) out.add(K_START);
        if (hit(rSelect, x, y)) out.add(K_SELECT);
    }

    private boolean hit(RectF r, float x, float y) {
        float p = r.height() * 0.2f;
        return x >= r.left - p && x <= r.right + p && y >= r.top - p && y <= r.bottom + p;
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

    private void arm(Canvas c, float l, float t, float r, float b, boolean on) {
        tmp.set(l, t, r, b);
        fill.setColor(Color.argb(on ? Math.min(255, alpha + 90) : alpha / 2, 255, 255, 255));
        c.drawRoundRect(tmp, 12f, 12f, fill);
        stroke.setColor(Color.argb(Math.min(255, alpha + 60), 255, 255, 255));
        stroke.setStrokeWidth(Math.max(2f, dpR * 0.03f));
        c.drawRoundRect(tmp, 12f, 12f, stroke);
    }

    private void box(Canvas c, RectF r, String label, boolean on) {
        fill.setColor(Color.argb(on ? Math.min(255, alpha + 90) : alpha / 2, 255, 255, 255));
        c.drawRoundRect(r, r.height() / 3f, r.height() / 3f, fill);
        stroke.setColor(Color.argb(Math.min(255, alpha + 60), 255, 255, 255));
        stroke.setStrokeWidth(Math.max(2f, r.height() * 0.05f));
        c.drawRoundRect(r, r.height() / 3f, r.height() / 3f, stroke);
        text.setColor(Color.argb(Math.min(255, alpha + 100), 255, 255, 255));
        text.setTextSize(r.height() * 0.45f);
        c.drawText(label, r.centerX(), r.centerY() - (text.ascent() + text.descent()) / 2f, text);
    }

    private void face(Canvas c, float cx, float cy, int kind, boolean on) {
        fill.setColor(Color.argb(on ? Math.min(255, alpha + 90) : alpha / 2, 255, 255, 255));
        c.drawCircle(cx, cy, fbR, fill);
        stroke.setColor(Color.argb(Math.min(255, alpha + 60), 255, 255, 255));
        stroke.setStrokeWidth(fbR * 0.08f);
        c.drawCircle(cx, cy, fbR, stroke);
        int cr = 255, cg = 255, cb = 255;
        if (kind == 0) { cr = 80; cg = 220; cb = 150; }
        else if (kind == 1) { cr = 255; cg = 90; cb = 90; }
        else if (kind == 2) { cr = 110; cg = 160; cb = 255; }
        else { cr = 240; cg = 130; cb = 220; }
        stroke.setColor(Color.argb(Math.min(255, alpha + 120), cr, cg, cb));
        stroke.setStrokeWidth(fbR * 0.14f);
        float s = fbR * 0.45f;
        if (kind == 0) {
            path.reset();
            path.moveTo(cx, cy - s);
            path.lineTo(cx + s, cy + s * 0.8f);
            path.lineTo(cx - s, cy + s * 0.8f);
            path.close();
            c.drawPath(path, stroke);
        } else if (kind == 1) {
            c.drawCircle(cx, cy, s, stroke);
        } else if (kind == 2) {
            c.drawLine(cx - s, cy - s, cx + s, cy + s, stroke);
            c.drawLine(cx - s, cy + s, cx + s, cy - s, stroke);
        } else {
            c.drawRect(cx - s, cy - s, cx + s, cy + s, stroke);
        }
    }

    @Override
    protected void onDraw(Canvas c) {
        float a = dpR * 0.34f;
        arm(c, dpCx - a, dpCy - dpR, dpCx + a, dpCy - a, down.contains(K_UP));
        arm(c, dpCx - a, dpCy + a, dpCx + a, dpCy + dpR, down.contains(K_DOWN));
        arm(c, dpCx - dpR, dpCy - a, dpCx - a, dpCy + a, down.contains(K_LEFT));
        arm(c, dpCx + a, dpCy - a, dpCx + dpR, dpCy + a, down.contains(K_RIGHT));
        arm(c, dpCx - a, dpCy - a, dpCx + a, dpCy + a, false);
        face(c, fbCx, fbCy - fbOff, 0, down.contains(K_TRIANGLE));
        face(c, fbCx + fbOff, fbCy, 1, down.contains(K_CIRCLE));
        face(c, fbCx, fbCy + fbOff, 2, down.contains(K_CROSS));
        face(c, fbCx - fbOff, fbCy, 3, down.contains(K_SQUARE));
        box(c, rL1, "L1", down.contains(K_L1));
        box(c, rL2, "L2", down.contains(K_L2));
        box(c, rR1, "R1", down.contains(K_R1));
        box(c, rR2, "R2", down.contains(K_R2));
        box(c, rSelect, "SELECT", down.contains(K_SELECT));
        box(c, rStart, "START", down.contains(K_START));
    }
}
