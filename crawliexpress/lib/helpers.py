import csv
import json
    
# Save .csv file from dict List [{}]
def save_file(results, filename, format):

        if(format=='csv'):
            if(len(results) > 0):
                with open(f'{filename}.csv', 'w', encoding='utf8', newline='') as output_file:
                    output_file.write('sep=,\n')
                    fc = csv.DictWriter(output_file, fieldnames=results[0].keys())
                    fc.writeheader()
                    fc.writerows(results)
        elif(format=='json'):
            with open(f'{filename}.json', 'w') as f:
                json.dump(results, f)

        print(f'file saved to {filename}.{format}')