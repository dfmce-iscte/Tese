from fuzzywuzzy import fuzz
import json
from bs4 import BeautifulSoup

# Similarity ratio is between 0 (no similarity) and 100 (similars)

index_of_technology_solutions = json.load(open('Index of Technology Solutions.json'))
technology_solutions = json.load(open('Scottish_technology_solutions_Complete.json', encoding='utf-8'))

for section_number, section in index_of_technology_solutions.items():
    for suplier, details in section['supliers'].items():
        if details['case_studies'] == ['']:
            # It means that there isn't case studies associated with the supplier or with the technology type
            continue

        if suplier == "Text":
            # It means that the case studies are associated with the technology type and not a specific supplier
            technology_solutions[section_number]['case_studies'] = details['case_studies']
        elif technology_solutions[section_number]['supliers'] != {}:
            # It means that the case studies are associated with a specific supplier.
            # In this case there is a need to obtain the supplier name from the technology solutions with a higher
            # similarity ratio since sometimes the names are not exactly the same.
            supliers_from_technology_solutions = list(technology_solutions[section_number]['supliers'].keys())
            supliers_from_technology_solutions_clean = \
                [BeautifulSoup(s, "html.parser").get_text().strip() for s in supliers_from_technology_solutions]

            higher_similarity_ratio = 0
            suplier_index = -1

            for i, s in enumerate(supliers_from_technology_solutions_clean):
                similarity_ratio = fuzz.ratio(suplier.lower().strip(), s.lower())
                if similarity_ratio > higher_similarity_ratio:
                    higher_similarity_ratio = similarity_ratio
                    suplier_index = i

            # print(f"\nNumber of supliers: {len(supliers_from_technology_solutions)}, Index: {suplier_index}")
            print(f"\nHigher Similarity Ratio: {higher_similarity_ratio}, {suplier} vs {supliers_from_technology_solutions_clean[suplier_index]}")
            suplier_key = supliers_from_technology_solutions[suplier_index]
            technology_solutions[section_number]['supliers'][suplier_key]['case_studies'] = details['case_studies']


with open('Technology Types with Case Studies.json', 'w') as file:
    file.write(json.dumps(technology_solutions, indent=4))

