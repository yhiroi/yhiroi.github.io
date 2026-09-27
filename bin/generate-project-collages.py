#!/usr/bin/env python3
"""Render the user-directed project mosaics from original research figures.

The explicit panels in _data/project_collage_sources.json preserve the chosen
subjects and their placement. Crops are applied only to collage copies.
"""
from pathlib import Path
import json
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1600, 1200


def build():
    config_path = ROOT / '_data/project_collage_sources.json'
    config = json.loads(config_path.read_text(encoding='utf-8'))
    series = json.loads((ROOT / '_data/research_series.yml').read_text(encoding='utf-8'))
    owners = {}
    out = ROOT / 'assets/img/project_collages'
    for project in series:
        settings = config['projects'][project['id']]
        panels = settings['panels']
        assert settings['images'] == [p['image'] for p in panels]
        canvas = Image.new('RGB', (WIDTH, HEIGHT), '#f2f3f4')
        blank_pixels = 0
        rendered = []
        for n, panel in enumerate(panels):
            source = config['sources'][panel['image']]
            key = source['key']
            assert key not in owners or owners[key] == project['id'], 'Work repeated across project collages'
            owners[key] = project['id']
            x, y, w, h = panel['box']
            assert 0 <= x < x + w <= WIDTH and 0 <= y < y + h <= HEIGHT
            for other in panels[n + 1:]:
                xx, yy, ww, hh = other['box']
                assert x + w <= xx or xx + ww <= x or y + h <= yy or yy + hh <= y, 'Overlapping panels'
            if 'background' in panel:
                canvas.paste(panel['background'], (x, y, x + w, y + h))
            image = Image.open(ROOT / source['path']).convert('RGB')
            if 'crop' in panel:
                left, top, right, bottom = panel['crop']
                assert 0 <= left < right <= 1 and 0 <= top < bottom <= 1
                image = image.crop((round(left * image.width), round(top * image.height),
                                    round(right * image.width), round(bottom * image.height)))
            if panel['fit'] == 'cover':
                fitted = ImageOps.fit(image, (w, h), Image.Resampling.LANCZOS,
                                      centering=tuple(panel.get('center', [.5, .5])))
            else:
                assert panel['fit'] == 'contain'
                fitted = ImageOps.contain(image, (w, h), Image.Resampling.LANCZOS)
            px, py = x + (w - fitted.width) // 2, y + (h - fitted.height) // 2
            canvas.paste(fitted, (px, py))
            if panel.get('label'):
                font_candidates = [Path('C:/Windows/Fonts/arialbd.ttf'), Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')]
                font_path = next((p for p in font_candidates if p.exists()), None)
                font = ImageFont.truetype(str(font_path), 36) if font_path else ImageFont.load_default(size=36)
                ImageDraw.Draw(canvas).text((x + 18, y + 14), panel['label'], font=font, fill='white', stroke_width=1, stroke_fill='black')
            blank_pixels += w * h - fitted.width * fitted.height
            rendered.append(dict(panel, rendered_box=[px, py, fitted.width, fitted.height]))
        for width in (800, 1600):
            output = canvas if width == WIDTH else canvas.resize((width, width * 3 // 4), Image.Resampling.LANCZOS)
            output.save(out / f"{project['id']}-{width}.webp", quality=86, method=6)
        settings['layout_result'] = {
            'size': [WIDTH, HEIGHT], 'packing_blank_fraction': round(blank_pixels / (WIDTH * HEIGHT), 4),
            'panels': rendered
        }
        print(f"{project['id']}: {len(panels)} panels, {blank_pixels / (WIDTH * HEIGHT):.1%} unused panel area")
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    build()
