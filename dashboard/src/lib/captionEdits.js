// A caption is a timed slot: changing its text must preserve all timestamps.
export function replaceCaptionText(captions, index, text) {
    return captions.map((caption, i) => i === index ? { ...caption, text } : caption);
}
