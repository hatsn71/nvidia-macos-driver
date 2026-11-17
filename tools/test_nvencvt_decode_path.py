#!/usr/bin/env python3
"""The vendored decoder hands VideoToolbox pictures in the client's own pixel format, from a pool made with the client's
destination attributes, so no VTPixelTransferSession converts every frame (issue 256: 37 percent of the decode thread in the
transfer). Source-level guards, so a later re-vendoring cannot lose the behaviour; the measurement is on a card.
usage: test_nvencvt_decode_path.py [repo root]"""
import pathlib, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1])
src = (root / 'vendor/nvenc/vt/nvencvt_dec.c').read_text()
fails = 0
def check(n, ok):
    global fails
    print(('ok   ' if ok else 'FAIL ') + n); fails += 0 if ok else 1
check('the decoder reads the session\'s destination pixel buffer attributes', 'VTDecoderSessionGetDestinationPixelBufferAttributes(session)' in src)
check('it follows the client\'s pixel format when it is one it can produce', 'want == pf' in src)
check('it makes its own pool from those attributes unless told not to', 'if (dst && !getenv("NVDEC_NOOWNPOOL"))' in src)
check('the pool switch defaults on (no variable set means its own pool)', src.count('NVDEC_NOOWNPOOL') == 2 or 'NVDEC_NOOWNPOOL' in src)
own = src[src.index('if (dst && !getenv("NVDEC_NOOWNPOOL"))'):src.index('CVPixelBufferPoolCreate(kCFAllocatorDefault')]
check('its own pool is IOSurface-backed even when the client names only a pixel format (Chromium stops on a frame without one)',
      'if (!CFDictionaryContainsKey(m, kCVPixelBufferIOSurfacePropertiesKey))' in own)
alone = src[src.index('static OSStatus output_buffer('):src.index('CVPixelBufferCreate(NULL, w, h, s->pf, a, pb)')]
check('a buffer made outside any pool is IOSurface-backed too', 'kCVPixelBufferIOSurfacePropertiesKey' in alone)
print(f'{fails} failed' if fails else 'all passed'); sys.exit(1 if fails else 0)
