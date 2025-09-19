# Japanese Product Dimension Translator

A Python program that translates Japanese product dimensions to English while preserving all numerical measurements.

## Features

- Translates Japanese clothing measurement terms to English
- Preserves all numerical dimensions (cm, mm, m)
- Handles multi-line content within single cells
- Processes CSV files with Japanese content in column A
- Outputs translated English content in column B
- **Smart Learning**: Automatically detects unknown Japanese terms
- **Interactive Learning**: Prompts for translations of new terms
- **Persistent Memory**: Saves learned translations for future use
- **Materials Translation**: Translates product materials from Japanese to English
- **Care Labels Translation**: Translates care instructions using comprehensive care labels dictionary
- **Content Splitting**: Automatically splits materials content into materials, care instructions, and country of origin
- Extensible translation dictionary

## Usage

### Basic Usage (with Learning)
```bash
python3 japanese_translator.py input_file.csv
```

### Specify Output File
```bash
python3 japanese_translator.py input_file.csv output_file.csv
```

### Skip Learning New Terms
```bash
python3 japanese_translator.py input_file.csv --no-learn
```

### Process Materials Column
```bash
python3 japanese_translator.py input_file.csv --materials-col=2
```
This will process materials in column C (index 2) and split them into:
- Column C: Original materials
- Column D: Translated materials  
- Column E: Care instructions (original)
- Column F: Care instructions (translated)
- Column G: Country of origin

### View Available Translations
```bash
python3 japanese_translator.py --list
```

## Smart Learning Features

### Automatic Detection
The program automatically detects Japanese terms it doesn't recognize and will prompt you to provide translations.

### Interactive Learning
When unknown terms are found, the program will:
1. Show you all the unknown Japanese terms
2. Prompt you to provide English translations
3. Save the new translations for future use
4. Re-translate the file with the newly learned terms

### Persistent Memory
All learned translations are saved to `learned_translations.json` and will be automatically loaded in future runs.

## Care Labels Translation

The program includes a comprehensive care labels dictionary (`care_labels.json`) with translations for common Japanese care instructions such as:

- ※洗濯機不可・手洗いのみ。 → Do not machine wash; hand wash only.
- ※ドライクリーニング不可。 → Do not dry clean.
- ※色移りする事がありますので、淡色のものと分けて洗ってください。 → Wash separately from light-colored items, as color transfer may occur.
- And many more...

Care instructions are automatically translated when processing materials columns.

## Example

**Input (Column A - Single Cell with Multi-line Content):**
```
a）総丈：66.2cm
b）股下：19cm
c）身幅：31cm
d）裄丈：37cm
フード丈：26.5cm
フード幅：21cm
```

**Output (Column B - Translated Multi-line Content):**
```
a）Total Length：66.2cm
b）Inseam：19cm
c）Body Width：31cm
d）Sleeve Length：37cm
Hood Length：26.5cm
Hood Width：21cm
```

The program preserves the exact formatting and line breaks while translating only the Japanese terms.

## Supported Translations

The program includes translations for common Japanese clothing measurement terms:

- 総丈 → Total Length
- 股下 → Inseam
- 身幅 → Body Width
- 裄丈 → Sleeve Length
- フード丈 → Hood Length
- フード幅 → Hood Width
- 肩幅 → Shoulder Width
- 胸囲 → Chest
- ウエスト → Waist
- ヒップ → Hip
- And many more...

## Adding New Translations

You can extend the translation dictionary by modifying the `translations` dictionary in the `JapaneseDimensionTranslator` class, or by using the `add_translation()` method programmatically.

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)
