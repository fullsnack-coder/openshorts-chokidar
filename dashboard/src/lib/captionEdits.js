// A caption is a timed slot: changing its text must preserve all timestamps.
export function replaceCaptionText(captions, index, text) {
    return captions.map((caption, i) => i === index ? { ...caption, text } : caption);
}

export function updateCaptionTime(captions, index, field, value, durationSec) {
    const ms = Math.round(Number(value) * 1000);
    const caption = { ...captions[index], [field]: ms };
    if (value.trim() === '' || !Number.isFinite(ms) || caption.startMs < 0 ||
        caption.endMs > durationSec * 1000 || caption.startMs >= caption.endMs) {
        throw new Error('El inicio debe ser menor que el fin y ambos deben estar dentro del clip.');
    }
    return captions.map((item, i) => i === index ? caption : item);
}

export function captionsToSrt(captions) {
    const time = (ms) => {
        const n = Math.max(0, Math.round(ms));
        return `${String(Math.floor(n / 3600000)).padStart(2, '0')}:${String(Math.floor(n / 60000) % 60).padStart(2, '0')}:${String(Math.floor(n / 1000) % 60).padStart(2, '0')},${String(n % 1000).padStart(3, '0')}`;
    };
    return captions.filter(c => c.text.trim()).slice().sort((a, b) => a.startMs - b.startMs)
        .map((c, i) => `${i + 1}\n${time(c.startMs)} --> ${time(c.endMs)}\n${c.text.trim()}`).join('\n\n');
}

export function insertCaption(captions, index, text, start, end, durationSec) {
    const startMs = Math.round(Number(start) * 1000);
    const endMs = Math.round(Number(end) * 1000);
    if (!text.trim()) throw new Error('Escribe el texto del nuevo subtítulo.');
    if (String(start).trim() === '' || String(end).trim() === '' ||
        !Number.isFinite(startMs) || !Number.isFinite(endMs) ||
        startMs < 0 || endMs > durationSec * 1000 || startMs >= endMs) {
        throw new Error('Indica un inicio menor que el fin, dentro del clip.');
    }
    if ((index > 0 && startMs < captions[index - 1].endMs) ||
        (index < captions.length && endMs > captions[index].startMs)) {
        throw new Error('El rango debe caber entre sus vecinos. Ajusta primero sus tiempos si necesitas más espacio.');
    }
    return [...captions.slice(0, index), { text: text.trim(), startMs, endMs, timestampMs: startMs, confidence: null }, ...captions.slice(index)];
}
