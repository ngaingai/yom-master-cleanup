#!/usr/bin/env python3
"""
Japanese to English Product Dimension Translator

This program reads a CSV file with Japanese product dimensions and translates
the Japanese terms to English while preserving all numerical measurements.
"""

import csv
import io
import json
import os
import re
import sys
from typing import Dict, List, Tuple, Set


class JapaneseDimensionTranslator:
    def __init__(self, 
                 translations_file: str = "learned_translations.json", 
                 care_labels_file: str = "care_labels.json"):
        # Translation dictionary for Japanese clothing measurement terms
        self.translations = {
            # Basic measurements
            '総丈': 'Total Length',
            '股下': 'Inseam',
            '身幅': 'Body Width',
            '裄丈': 'Sleeve Length',
            'フード丈': 'Hood Length',
            'フード幅': 'Hood Width',
            '肩幅': 'Shoulder Width',
            '胸囲': 'Chest',
            'ウエスト': 'Waist',
            'ヒップ': 'Hip',
            '袖丈': 'Sleeve Length',
            '袖口': 'Cuff',
            '裾幅': 'Hem Width',
            '股上': 'Rise',
            '太もも': 'Thigh',
            '膝下': 'Knee',
            '足首': 'Ankle',
            
            # Additional common terms
            '丈': 'Length',
            '幅': 'Width',
            'cm': 'cm',  # Keep cm as is
            'mm': 'mm',  # Keep mm as is
            'm': 'm',    # Keep m as is
            
            # Common materials
            'コットン': 'Cotton',
            '綿': 'Cotton',
            'ポリエステル': 'Polyester',
            'ナイロン': 'Nylon',
            'ウール': 'Wool',
            'シルク': 'Silk',
            'レーヨン': 'Rayon',
            'アクリル': 'Acrylic',
            'スパンデックス': 'Spandex',
            'エラスタン': 'Elastane',
            'リネン': 'Linen',
            'カシミア': 'Cashmere',
            'モヘア': 'Mohair',
            'アルパカ': 'Alpaca',
            '混紡': 'Blend',
            '100%': '100%',
            
            # Additional material terms
            '表生地': 'Main Fabric',
            '裏生地': 'Lining Fabric',
            '刺繍糸': 'Embroidery Thread',
            '再生繊維': 'Regenerated Fiber',
            'セルロース': 'Cellulose',
            'ポリウレタン': 'Polyurethane',
        }
        
        # File to store learned translations
        self.translations_file = translations_file
        self.care_labels_file = care_labels_file
        self.unknown_terms: Set[str] = set()
        
        # Load previously learned translations and care labels
        self.load_learned_translations()
        self.load_care_labels()
    
    def convert_fullwidth_to_halfwidth(self, text: str) -> str:
        """
        Convert full-width characters to half-width equivalents.
        
        Args:
            text: Text containing full-width characters
            
        Returns:
            Text with full-width characters converted to half-width
        """
        if not text:
            return text
        
        # Full-width to half-width character mapping
        fullwidth_to_halfwidth = {
            # Parentheses and brackets
            '（': '(',
            '）': ')',
            '［': '[',
            '］': ']',
            '｛': '{',
            '｝': '}',
            
            # Punctuation
            '：': ':',
            '；': ';',
            '，': ',',
            '、': ',',
            '．': '.',
            '！': '!',
            '？': '?',
            '～': ' to ',
            '－': '-',
            '＿': '_',
            '＝': '=',
            '＋': '+',
            '＊': '*',
            '／': '/',
            '＼': '\\',
            '｜': '|',
            '＠': '@',
            '＃': '#',
            '＄': '$',
            '％': '%',
            '＾': '^',
            '＆': '&',
            
            # Numbers
            '０': '0',
            '１': '1',
            '２': '2',
            '３': '3',
            '４': '4',
            '５': '5',
            '６': '6',
            '７': '7',
            '８': '8',
            '９': '9',
            
            # Letters (uppercase)
            'Ａ': 'A',
            'Ｂ': 'B',
            'Ｃ': 'C',
            'Ｄ': 'D',
            'Ｅ': 'E',
            'Ｆ': 'F',
            'Ｇ': 'G',
            'Ｈ': 'H',
            'Ｉ': 'I',
            'Ｊ': 'J',
            'Ｋ': 'K',
            'Ｌ': 'L',
            'Ｍ': 'M',
            'Ｎ': 'N',
            'Ｏ': 'O',
            'Ｐ': 'P',
            'Ｑ': 'Q',
            'Ｒ': 'R',
            'Ｓ': 'S',
            'Ｔ': 'T',
            'Ｕ': 'U',
            'Ｖ': 'V',
            'Ｗ': 'W',
            'Ｘ': 'X',
            'Ｙ': 'Y',
            'Ｚ': 'Z',
            
            # Letters (lowercase)
            'ａ': 'a',
            'ｂ': 'b',
            'ｃ': 'c',
            'ｄ': 'd',
            'ｅ': 'e',
            'ｆ': 'f',
            'ｇ': 'g',
            'ｈ': 'h',
            'ｉ': 'i',
            'ｊ': 'j',
            'ｋ': 'k',
            'ｌ': 'l',
            'ｍ': 'm',
            'ｎ': 'n',
            'ｏ': 'o',
            'ｐ': 'p',
            'ｑ': 'q',
            'ｒ': 'r',
            'ｓ': 's',
            'ｔ': 't',
            'ｕ': 'u',
            'ｖ': 'v',
            'ｗ': 'w',
            'ｘ': 'x',
            'ｙ': 'y',
            'ｚ': 'z',
        }
        
        # Convert full-width characters to half-width
        converted_text = text
        for fullwidth, halfwidth in fullwidth_to_halfwidth.items():
            converted_text = converted_text.replace(fullwidth, halfwidth)
        
        return converted_text
    
    def add_spacing_after_punctuation(self, text: str) -> str:
        """
        Add spaces after specific punctuation marks for better readability.
        
        Args:
            text: Text to format
            
        Returns:
            Text with spaces added after ), , and :
        """
        if not text:
            return text
        
        # Add spaces after ), , and : (but not if already followed by a space)
        formatted_text = text
        
        # Add space after ) if not already followed by space or newline
        formatted_text = re.sub(r'\)(?![\s\n])', ') ', formatted_text)
        
        # Add space after , if not already followed by space or newline
        formatted_text = re.sub(r',(?![\s\n])', ', ', formatted_text)
        
        # Add space after : if not already followed by space or newline
        formatted_text = re.sub(r':(?![\s\n])', ': ', formatted_text)
        
        return formatted_text
    
    def add_spaces_after_materials(self, text: str) -> str:
        """
        Add spaces between translated materials and percentages/numbers.
        
        Args:
            text: Text containing material translations
            
        Returns:
            Text with spaces added after materials before percentages
        """
        if not text:
            return text
        
        # Add space between material names and percentages/numbers
        # Pattern: MaterialName followed by number or percentage
        formatted_text = re.sub(r'([A-Za-z]+)(\d+%)', r'\1 \2', text)
        formatted_text = re.sub(r'([A-Za-z]+)(\d+)', r'\1 \2', formatted_text)
        
        return formatted_text
    
    def split_materials_content(self, content: str) -> tuple:
        """
        Split content into materials, care instructions, and country of origin.
        
        Args:
            content: Full cell content containing materials, care instructions, and country
            
        Returns:
            Tuple of (materials, care_instructions, country)
        """
        if not content:
            return "", "", ""
        
        lines = content.strip().split('\n')
        
        # Find the first line with ※
        first_asterisk_index = -1
        for i, line in enumerate(lines):
            if '※' in line:
                first_asterisk_index = i
                break
        
        if first_asterisk_index == -1:
            # No ※ found, treat everything as materials
            return content.strip(), "", ""
        
        # Split content
        materials_lines = lines[:first_asterisk_index]
        care_and_country_lines = lines[first_asterisk_index:]
        
        # Extract materials (everything before first ※)
        materials = '\n'.join(materials_lines).strip()
        
        # Find country of origin (last line that doesn't start with ※)
        country = ""
        care_lines = []
        
        for line in care_and_country_lines:
            if line.strip() and not line.strip().startswith('※'):
                country = line.strip()
            else:
                care_lines.append(line)
        
        # Extract care instructions (everything from first ※ to last ※)
        care_instructions = '\n'.join(care_lines).strip()
        
        return materials, care_instructions, country
    
    def translate_care_instructions(self, care_instructions: str) -> str:
        """
        Translate care instructions using the care labels dictionary.
        
        Args:
            care_instructions: Japanese care instructions text
            
        Returns:
            Translated English care instructions
        """
        if not care_instructions or not isinstance(care_instructions, str):
            return care_instructions
        
        # Start with the original text
        translated_text = care_instructions
        
        # Replace care label terms with English equivalents
        # Sort by length (longest first) to prevent partial translations
        sorted_care_labels = sorted(
            self.care_labels.items(), 
            key=lambda x: len(x[0]), 
            reverse=True
        )
        for japanese, english in sorted_care_labels:
            translated_text = translated_text.replace(japanese, english)
        
        return translated_text
    
    def load_learned_translations(self) -> None:
        """Load previously learned translations from file."""
        if os.path.exists(self.translations_file):
            try:
                with open(self.translations_file, 'r', encoding='utf-8') as f:
                    learned = json.load(f)
                    self.translations.update(learned)
                    print(f"Loaded {len(learned)} previously learned translations.")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load learned translations: {e}")
    
    def load_care_labels(self) -> None:
        """Load care label translations from file."""
        if os.path.exists(self.care_labels_file):
            try:
                with open(self.care_labels_file, 'r', encoding='utf-8') as f:
                    self.care_labels = json.load(f)
                    print(f"Loaded {len(self.care_labels)} care label translations.")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load care labels: {e}")
                self.care_labels = {}
        else:
            self.care_labels = {}
    
    def save_learned_translations(self) -> None:
        """Save learned translations to file, sorted by length (longest first)."""
        try:
            # Sort translations by length (longest first) for better organization
            sorted_translations = dict(
                sorted(self.translations.items(), key=lambda x: len(x[0]), reverse=True)
            )
            with open(self.translations_file, 'w', encoding='utf-8') as f:
                json.dump(sorted_translations, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Warning: Could not save learned translations: {e}")
    
    def extract_japanese_terms(self, text: str) -> Set[str]:
        """Extract potential Japanese terms from text."""
        # Pattern to match Japanese characters (Hiragana, Katakana, Kanji)
        japanese_pattern = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+'
        terms = set(re.findall(japanese_pattern, text))
        
        # Filter out known terms and measurements
        unknown_terms = set()
        for term in terms:
            if term not in self.translations and len(term) > 1:
                # Skip if it's just a measurement unit or number
                if not re.match(r'^[0-9.,：:cm]+$', term):
                    unknown_terms.add(term)
        
        return unknown_terms
    
    def learn_new_translation(self, japanese: str, english: str) -> None:
        """Learn a new translation and save it."""
        self.translations[japanese] = english
        self.save_learned_translations()
        print(f"✓ Learned: '{japanese}' -> '{english}'")
    
    def interactive_learning(self, unknown_terms: Set[str]) -> None:
        """Interactively learn translations for unknown terms."""
        if not unknown_terms:
            return
        
        print(f"\n🔍 Found {len(unknown_terms)} unknown Japanese terms:")
        for term in sorted(unknown_terms):
            print(f"  - {term}")
        
        print(f"\n📚 Learning new translations (press Enter to skip a term):")
        
        for term in sorted(unknown_terms):
            while True:
                translation = input(f"'{term}' → ").strip()
                
                if not translation:
                    print(f"  Skipped '{term}'")
                    break
                elif translation.lower() in ['skip', 's']:
                    print(f"  Skipped '{term}'")
                    break
                else:
                    self.learn_new_translation(term, translation)
                    break
    
    def translate_text(self, text: str, interactive: bool = True) -> str:
        """
        Translate Japanese text to English while preserving measurements.
        Handles multi-line content within a single cell.
        
        Args:
            text: Japanese text containing measurements (can be multi-line)
            interactive: Whether to interactively learn new terms
            
        Returns:
            Translated English text with preserved measurements and formatting
        """
        if not text or not isinstance(text, str):
            return text
        
        # Extract unknown Japanese terms if in interactive mode
        if interactive:
            unknown_terms = self.extract_japanese_terms(text)
            if unknown_terms:
                self.unknown_terms.update(unknown_terms)
        
        # Split into lines to handle multi-line content
        lines = text.split('\n')
        translated_lines = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                translated_lines.append(line)
                continue
            
            # Start with the original line
            translated_line = line
            
            # Replace Japanese terms with English equivalents
            # Sort by length (longest first) to prevent partial translations
            sorted_translations = sorted(
                self.translations.items(), 
                key=lambda x: len(x[0]), 
                reverse=True
            )
            for japanese, english in sorted_translations:
                translated_line = translated_line.replace(japanese, english)
            
            translated_lines.append(translated_line)
        
        # Join lines back together
        translated_text = '\n'.join(translated_lines)
        
        # Convert full-width characters to half-width
        translated_text = self.convert_fullwidth_to_halfwidth(translated_text)
        
        # Add spacing after punctuation for better readability
        translated_text = self.add_spacing_after_punctuation(translated_text)
        
        # Add spaces between materials and percentages
        translated_text = self.add_spaces_after_materials(translated_text)
        
        return translated_text
    
    def process_csv_file(self, 
                        input_file: str, 
                        output_file: str = None, 
                        interactive: bool = True, 
                        materials_column: int = 1) -> None:
        """
        Process a CSV file and translate Japanese content.
        Input: Column A = Japanese dimensions, Column B = Japanese materials
        Output: A=Japanese dimensions, B=English dimensions, C=Japanese materials, 
                D=English materials, E=Japanese care labels, F=English care labels, G=country
        
        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file (optional, defaults to input_file_translated.csv)
            interactive: Whether to interactively learn new terms
            materials_column: Which column (0-based index) contains materials to translate 
                              (default: 1, which is column B)
        """
        if output_file is None:
            # Create output filename based on input filename
            base_name = input_file.rsplit('.', 1)[0]
            output_file = f"{base_name}_translated.csv"
        
        try:
            with open(input_file, 'r', encoding='utf-8') as infile:
                # Read the entire file content first
                content = infile.read()
                
                # Try to detect the delimiter from a sample
                sample = content[:1024] if len(content) > 1024 else content
                sniffer = csv.Sniffer()
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                    # If delimiter is not comma, use comma as default
                    if delimiter != ',':
                        delimiter = ','
                except:
                    delimiter = ','
                
                # Use StringIO to properly parse the CSV content
                csv_reader = csv.reader(io.StringIO(content), delimiter=delimiter, quoting=csv.QUOTE_ALL)
                
                with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                    writer = csv.writer(outfile, delimiter=delimiter, quoting=csv.QUOTE_ALL, lineterminator='\n')
                    
                    # Process each CSV row
                    for row_num, row in enumerate(csv_reader, 1):
                        if not row:
                            # Empty row
                            writer.writerow([''])
                            continue
                        
                        # Ensure we have at least column A
                        if len(row) < 1:
                            writer.writerow([''])
                            continue
                        
                        # Get the Japanese content from column A (dimensions)
                        japanese_dimensions = row[0]
                        
                        # Translate dimensions to English
                        english_dimensions = self.translate_text(japanese_dimensions, interactive)
                        
                        # Handle materials column (if present and specified)
                        if len(row) > materials_column:
                            full_materials_content = row[materials_column]
                            
                            # Split the content into materials, care instructions, and country
                            materials_content, care_instructions, country = self.split_materials_content(
                                full_materials_content
                            )
                            
                            # Translate materials to English
                            materials_english = self.translate_text(materials_content, interactive)
                            
                            # Translate care instructions to English
                            care_instructions_english = self.translate_care_instructions(care_instructions)
                            
                            # Create new row with the correct output format:
                            # A=Japanese dimensions, B=English dimensions, C=Japanese materials, 
                            # D=English materials, E=Japanese care labels, F=English care labels, G=country
                            new_row = [
                                japanese_dimensions,      # A: Japanese dimensions
                                english_dimensions,       # B: English dimensions
                                materials_content,        # C: Japanese materials
                                materials_english,        # D: English materials
                                care_instructions,        # E: Japanese care labels
                                care_instructions_english, # F: English care labels
                                country                   # G: Country of origin
                            ]
                        else:
                            # No materials column, just dimensions
                            new_row = [japanese_dimensions, english_dimensions]
                        
                        writer.writerow(new_row)
                        
                        # Print progress for first few rows
                        if row_num <= 5:
                            print(f"Row {row_num}:")
                            print(f"  Japanese Dimensions: {japanese_dimensions}")
                            print(f"  English Dimensions:  {english_dimensions}")
                            if len(row) > materials_column:
                                print(f"  Japanese Materials: {materials_content}")
                                print(f"  English Materials: {materials_english}")
                                if care_instructions:
                                    print(f"  Japanese Care Instructions: {care_instructions[:50]}...")
                                    print(f"  English Care Instructions: "
                                          f"{care_instructions_english[:50]}...")
                                if country:
                                    print(f"  Country: {country}")
                            print()
            
            # Handle unknown terms if in interactive mode
            if interactive and self.unknown_terms:
                self.interactive_learning(self.unknown_terms)
                
                # Re-translate with newly learned terms
                print("\n🔄 Re-translating with newly learned terms...")
                with open(input_file, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    csv_reader = csv.reader(io.StringIO(content), delimiter=delimiter, quoting=csv.QUOTE_ALL)
                    
                    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
                        writer = csv.writer(outfile, delimiter=delimiter, quoting=csv.QUOTE_ALL, lineterminator='\n')
                        
                        for row in csv_reader:
                            if not row or len(row) < 1:
                                writer.writerow([''])
                                continue
                            
                            # Get the Japanese content from column A (dimensions)
                            japanese_dimensions = row[0]
                            
                            # Translate dimensions to English
                            english_dimensions = self.translate_text(japanese_dimensions, interactive=False)
                            
                            # Handle materials column (if present and specified)
                            if len(row) > materials_column:
                                full_materials_content = row[materials_column]
                                
                                # Split the content into materials, care instructions, and country
                                materials_content, care_instructions, country = self.split_materials_content(
                                    full_materials_content
                                )
                                
                                # Translate materials to English
                                materials_english = self.translate_text(materials_content, interactive=False)
                                
                                # Translate care instructions to English
                                care_instructions_english = self.translate_care_instructions(care_instructions)
                                
                                # Create new row with the correct output format:
                                # A=Japanese dimensions, B=English dimensions, C=Japanese materials, 
                                # D=English materials, E=Japanese care labels, F=English care labels, G=country
                                new_row = [
                                    japanese_dimensions,      # A: Japanese dimensions
                                    english_dimensions,       # B: English dimensions
                                    materials_content,        # C: Japanese materials
                                    materials_english,        # D: English materials
                                    care_instructions,        # E: Japanese care labels
                                    care_instructions_english, # F: English care labels
                                    country                   # G: Country of origin
                                ]
                            else:
                                # No materials column, just dimensions
                                new_row = [japanese_dimensions, english_dimensions]
                            
                            writer.writerow(new_row)
            
            print(f"Translation complete! Output saved to: {output_file}")
            
        except FileNotFoundError:
            print(f"Error: Input file '{input_file}' not found.")
            sys.exit(1)
        except Exception as e:
            print(f"Error processing file: {e}")
            sys.exit(1)
    
    def add_translation(self, japanese: str, english: str) -> None:
        """
        Add a new translation to the dictionary.
        
        Args:
            japanese: Japanese term
            english: English translation
        """
        self.translations[japanese] = english
        print(f"Added translation: '{japanese}' -> '{english}'")
    
    def list_translations(self) -> None:
        """Print all available translations."""
        print("Available translations:")
        for japanese, english in sorted(self.translations.items()):
            print(f"  {japanese} -> {english}")


def main():
    """Main function to run the translator."""
    translator = JapaneseDimensionTranslator()
    
    if len(sys.argv) < 2:
        print("Usage: python japanese_translator.py <input_csv_file> [output_csv_file] "
              "[--no-learn] [--materials-col=<number>]")
        print("\nExample:")
        print("  python japanese_translator.py products.csv")
        print("  python japanese_translator.py products.csv translated_products.csv")
        print("  python japanese_translator.py products.csv --no-learn  # Skip learning new terms")
        print("  python japanese_translator.py products.csv --materials-col=1  # Materials in column B (default)")
        print("  python japanese_translator.py products.csv --materials-col=2  # Materials in column C")
        print("\nTo see available translations:")
        print("  python japanese_translator.py --list")
        sys.exit(1)
    
    if sys.argv[1] == "--list":
        translator.list_translations()
        return
    
    # Parse arguments
    input_file = sys.argv[1]
    output_file = None
    interactive = True
    materials_column = 1  # Default to column B (index 1)
    
    for arg in sys.argv[2:]:
        if arg == "--no-learn":
            interactive = False
        elif arg.startswith("--materials-col="):
            try:
                materials_column = int(arg.split("=")[1]) - 1  # Convert to 0-based index
            except (ValueError, IndexError):
                print(f"Error: Invalid materials column number: {arg}")
                sys.exit(1)
        elif not arg.startswith("--"):
            output_file = arg
    
    print(f"Processing file: {input_file}")
    if not interactive:
        print("Learning mode: DISABLED (using existing translations only)")
    else:
        print("Learning mode: ENABLED (will learn new terms interactively)")
    print(f"Materials column: {materials_column + 1} "
          f"(Column {chr(65 + materials_column + 1)})")
    
    translator.process_csv_file(input_file, output_file, interactive, materials_column)


if __name__ == "__main__":
    main()
