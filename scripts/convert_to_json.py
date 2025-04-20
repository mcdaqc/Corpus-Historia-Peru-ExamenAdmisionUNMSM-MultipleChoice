import re
import json
import os

def parse_answers_file(file_path):
    """
    Parse the claves.txt file to extract the correct answers
    """
    # Letter to index mapping
    letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4}
    
    # Dictionary to store the answers (question_num: answer_index)
    answers = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract answers line by line to ensure we capture everything
    for line in content.split('\n'):
        if '|' not in line or line.startswith('# Claves') or ':--:' in line:
            continue  # Skip header lines or non-data lines
        
        # Find all pairs of question numbers and answers in the line
        pairs = re.findall(r'\|\s*(\d+)\s*\|\s*([A-E])\s*', line)
        
        for question_num, letter in pairs:
            question_num = int(question_num)
            answers[question_num] = letter_to_index.get(letter, 0)
    
    # Debug: Print the number of answers and some examples
    print(f"Extracted {len(answers)} answers from claves.txt")
    print(f"Sample answers: 405: {answers.get(405, 'Not found')}, 406: {answers.get(406, 'Not found')}, 449: {answers.get(449, 'Not found')}")
    
    return answers

def parse_categories(content):
    """
    Split the content by categories marked with ## and return a dictionary
    mapping category names to their English translations
    """
    # Dictionary to translate categories from Spanish to English
    category_translations = {
        "CONCEPTOS GENERALES DE HISTORIA": "General Concepts of History",
        "POBLAMIENTO DE AMÉRICA": "Population of America",
        "POBLAMIENTO ANDINO": "Andean Settlement",
        "HORIZONTE TEMPRANO: CHAVIN": "Early Horizon: Chavin",
        "PARACAS - VICUS- PUEARA": "Paracas - Vicus - Pucara",
        "INTERMEDIO TEMPRANO: NAZCA, LIMA": "Early Intermediate: Nazca, Lima",
        "MOCHE, LAMBAYEQUE, RECUAY": "Moche, Lambayeque, Recuay",
        "NOEIG LAMBANECUS, BEZUAY": "Moche, Lambayeque, Recuay",
        "HORIZONTE MEDIO: TIAHUANACO": "Middle Horizon: Tiahuanaco",
        "HORIZONTE MEDIO: WARI": "Middle Horizon: Wari",
        "HORIZONTE MEDICA WARI": "Middle Horizon: Wari",
        "INTERMEDIO TARDIO: CHIMÚ, CHINCHAS": "Late Intermediate: Chimu, Chinchas",
        "INTERMEDICI TARIÓN CRIAU CRIRCIAS": "Late Intermediate: Chimu",
        "CHANCAS, AYMARAS": "Chancas, Aymaras",
        "TAHUANTINSUYO: SOCIEDAD Y POLÍTICA": "Tahuantinsuyo: Society and Politics",
        "TAHUANTINSUYO: ECONOMÍA Y CULTURA": "Tahuantinsuyo: Economy and Culture",
        "EXPANSIÓN EUROPEA": "European Expansion",
        "INVANSIÓN AL TAHUANTINSUYO": "Invasion of Tahuantinsuyo",
        "RESISTENCIA ANDINA": "Andean Resistance",
        "GUERRAS CIVILES": "Civil Wars",
        "VIRREINATO PERUANO: SOCIEDAD Y POLÍTICA": "Peruvian Viceroyalty: Society and Politics",
        "VIRREINATO PERUANO: ECONOMÍA Y CULTURA": "Peruvian Viceroyalty: Economy and Culture",
        "PROCESO DE LA EMANCIPACIÓN. REFORMAS BORBÓNICAS. REBELIONES INDÍGENES": "Emancipation Process. Bourbon Reforms. Indigenous Rebellions",
        "PRECURSORES Y PRÓCERES - CRISIS POLÍTICA ESPÁNOLA": "Precursors and Heroes - Spanish Political Crisis",
        "CORRIENTE LIBERTADORA DEL SUR": "Southern Liberation Current",
        "CORRIENTE LIBERTADORA DEL NORTE": "Northern Liberation Current",
        "PERÚ REPUBLICANO: PRIMER MILITARISMO": "Republican Peru: First Militarism",
        "CONFEDERACIÓN PERUANO - BOLIVIANA, ANARQUÍA MILITAR": "Peruvian-Bolivian Confederation, Military Anarchy",
        "PROSPERIDAD FALAZ": "Fallacious Prosperity",
        "GUERRA CON ESPAÑA - CIVILISMO": "War with Spain - Civilism",
        "GUERRA CON CHILE": "War with Chile",
        "SEGUNDO MILITARISMO Y RECONSTRUCCIÓN NACIONAL": "Second Militarism and National Reconstruction",
        "REPÚBLICA ARISTOCRÁTICA": "Aristocratic Republic",
        "ONCENIO DE LEGUIA (1919-1930)": "Leguia's Eleven-Year Rule (1919-1930)",
        "TERCER MILITARISMO": "Third Militarism",
        "OCHENIO DE MANUEL A. ODRÍA": "Manuel A. Odria's Eight-Year Rule",
        "REPUBLICA. SEGUNDA MITAD DEL SIGLO XX. VELASQUISMO": "Republic. Second Half of the 20th Century. Velasquismo",
        "RESTAURACIÓN DEMOCRÁTICA. BELAUNDE, GARCÍA, FUJIMORI, TOLEDO, OLLANTA": "Democratic Restoration. Belaunde, Garcia, Fujimori, Toledo, Ollanta",
        "MAYAS, AZTECAS, CHOROTECAS": "Maya, Aztec, Chorotec",
        "MAYAS ASTRUAS CHOROTECAS": "Maya, Aztec, Chorotec",
    }
    
    # Find all category markers
    category_pattern = r'##\s*(.*?)(?=\n)'
    categories = re.findall(category_pattern, content)
    
    # Split content by categories
    category_sections = {}
    current_category = None
    
    for line in content.split('\n'):
        if line.strip().startswith('##'):
            current_category = line.replace('##', '').strip()
            category_sections[current_category] = []
        elif current_category:
            category_sections[current_category].append(line)
    
    # Create a dictionary mapping category names to their translations
    result = {}
    for category in category_sections:
        en_name = category_translations.get(category, category)
        result[category] = {
            'content': category_sections[category],
            'category_en': en_name,
            'category_original_lang': category
        }
    
    return result

def extract_questions(content, answers):
    """
    Extract questions and options from the content
    """
    result = []
    
    # Split content by categories
    categories = parse_categories(content)
    
    for category, data in categories.items():
        category_lines = data['content']
        current_question = None
        current_options = []
        current_question_num = None
        
        for line in category_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a question
            question_match = re.match(r'^(\d+)\.\s+(.*?)$', line)
            if question_match:
                # If we've been processing a question, save it
                if current_question and current_options:
                    # Use -1 if no answer is available
                    answer_value = answers.get(current_question_num, -1)
                    
                    question_item = {
                        "language": "es",
                        "country": "Perú",
                        "exam_name": "Solucionario Exámenes de Admisión, Historia del Peru - Universidad Nacional Mayor de San Marcos",
                        "source": "https://www.slideshare.net/slideshow/historia-del-per-recopilacin-ex-adm-unmsm/251464302",
                        "license": "Desconocida",
                        "level": "Acceso a la Universidad",
                        "category_en": data['category_en'],
                        "category_original_lang": data['category_original_lang'],
                        "original_question_num": current_question_num,
                        "question": current_question,
                        "options": current_options,
                        "answer": answer_value
                    }
                    result.append(question_item)
                
                # Start processing new question
                current_question_num = int(question_match.group(1))
                current_question = question_match.group(2)
                current_options = []
            
            # Check if this is an option
            option_match = re.match(r'^([A-E])\)\s+(.*?)$', line)
            if option_match and current_question:
                option_text = option_match.group(2)
                current_options.append(option_text)
        
        # Don't forget to save the last question of each category
        if current_question and current_options:
            # Use -1 if no answer is available
            answer_value = answers.get(current_question_num, -1)
            
            question_item = {
                "language": "es",
                "country": "Perú",
                "exam_name": "Solucionario Exámenes de Admisión, Historia del Peru - Universidad Nacional Mayor de San Marcos",
                "source": "https://www.slideshare.net/slideshow/historia-del-per-recopilacin-ex-adm-unmsm/251464302",
                "license": "Desconocida",
                "level": "Acceso a la Universidad",
                "category_en": data['category_en'],
                "category_original_lang": data['category_original_lang'],
                "original_question_num": current_question_num,
                "question": current_question,
                "options": current_options,
                "answer": answer_value
            }
            result.append(question_item)
    
    return result

def main():
    """
    Main function to convert the files
    """
    # File paths
    questions_file = "files/data_clean/cuestionario.txt"
    answers_file = "files/data_clean/claves.txt"
    output_file = "cuestionario.json"
    
    # Check if files exist
    if not os.path.exists(questions_file):
        print(f"Error: File {questions_file} not found!")
        return
    
    if not os.path.exists(answers_file):
        print(f"Error: File {answers_file} not found!")
        return
    
    # Parse answers
    answers = parse_answers_file(answers_file)
    
    # Read questions
    with open(questions_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract questions and options
    result = extract_questions(content, answers)
    
    # Count questions without answers
    no_answer_count = sum(1 for q in result if q["answer"] == -1)
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Conversion completed! {len(result)} questions saved to {output_file}")
    print(f"Questions with no answer: {no_answer_count}")

if __name__ == "__main__":
    main() 