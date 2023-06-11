import requests, csv, os, math, json, datetime, locale
from bs4 import BeautifulSoup
def ListMaker():
    print("    Parsing HTML (1/6)")
    url = 'https://inara.cz/elite/commodities-list/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    print("    Finding & Extracting Table (2/6)")
    table = soup.find('table')
    rows = table.find_all('tr')
    row_data_list = []
    string_list = []
    print("    Processing Table (3/6)")
    for row in rows:
        cells = row.find_all('td')
        try:
            cell_texts = [cell.get_text(strip=True).replace(',', '') for cell in cells]
            if all(cell_texts) and all(int(value.replace('Cr', '')) != 0 for value in cell_texts[1:3]):
                modified_row_data = [
                    cell_texts[0],
                    int(cell_texts[-1].replace('Cr', ''))
                ]
                row_data_list.append(modified_row_data)
        except IndexError:
            continue
    print("    Creating Commodity List (4/6)")
    for row_data in row_data_list:
        string_list.append(row_data[0])
    data = []
    existing_terms = set()
    with open("!Commodities.csv", 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            term = row['Term']
            existing_terms.add(term)
    print("    Uploading list to .csv file (5/6)")
    for term in string_list:
        if term in existing_terms:
            continue
        number = input(f"    -    Enter a number for '{term}': ")
        data.append([term, number])
    with open("!Commodities.csv", 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    print("    .csv file saved (6/6)")
def ImportCommodityData():
    print("    Grabbing list of Commodities (1/3)")
    with open("!Commodities.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader)
        print("    Getting all commodity data and saving to files (2/3)")
        for row in reader:
            term, number = row
            link = f"https://inara.cz/elite/commodities/?pi1=1&pa1%5B%5D={number}&ps1=Sol&pi10=2&pi11=0&pi3=1&pi9=0&pi4=2&pi5=720&pi12=0&pi7=0&pi8=1"
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table is None:
                print(f"    -    No table found for {term}")
                continue
            csv_file_path = f"{term}Import.csv"
            if os.path.exists(csv_file_path):
                os.remove(csv_file_path)
            with open(csv_file_path, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    cell_texts = [cell.get_text(strip=True).replace(',', '').replace('\uFFFD', "").replace('\ue84d', "").replace("\ue81d",'').replace("\ufe0e",'').replace("︎",'').replace('\ue84f', "").replace('\ue81d', "").replace('\ue84e', "").replace('\ue823', '') for cell in cells]
                    writer.writerow(cell_texts)
        print("    All files saved (3/3)")
def EditImCommodityData():
    print("    Indexing all files to be edited (1/3)")
    csv_files = [file for file in os.listdir('.') if file.endswith('Import.csv')]
    print("    Editing  & removing Files (2/3)")
    for file in csv_files:
        with open(file, 'r') as csv_file:
            rows = csv.reader(csv_file)
            modified_rows = []
            for row in rows:
                if row:
                    modified_row = [row[0], *row[4:6]]
                    modified_row[2] = modified_row[2].replace('Cr', '')
                    if int(modified_row[1]) >= 20000:
                        modified_rows.append(modified_row)
        with open(file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(modified_rows)
        if os.stat(file).st_size == 0:
            os.remove(file)
            print(f"    -    {os.path.splitext(file)[0].replace('Import','')} removed due to insufficient stock")
    print("    All files edited & (3/3)")
def ExportCommodityData():
    print("    Grabbing list of Commodities (1/3)")
    with open("!Commodities.csv", 'r') as file:
        reader = csv.reader(file)
        next(reader)
        print("    Getting all commodity data and saving to files (2/3)")
        for row in reader:
            term, number = row
            link = f"https://inara.cz/elite/commodities/?pi1=2&pa1%5B%5D={number}&ps1=Sol&pi10=2&pi11=0&pi3=1&pi9=0&pi4=2&pi5=720&pi12=0&pi7=0&pi8=1"
            response = requests.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table')
            if table is None:
                print(f"    -    No table found for {term}")
                continue
            csv_file_path = f"{term}Export.csv"
            if os.path.exists(csv_file_path):
                os.remove(csv_file_path)
            with open(csv_file_path, 'a', newline='') as csv_file:
                writer = csv.writer(csv_file)
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    cell_texts = [cell.get_text(strip=True).replace(',', '').replace('\uFFFD', "").replace('\ue84d', "").replace("\ue81d",'').replace("\ufe0e",'').replace("︎",'').replace('\ue84f', "").replace('\ue81d', "").replace('\ue84e', "").replace('\ue823', '') for cell in cells]
                    writer.writerow(cell_texts)
        print("    All files saved (3/3)")
def EditExCommodityData():
    print("    Indexing all files to be edited (1/3)")
    csv_files = [file for file in os.listdir('.') if file.endswith('Export.csv')]
    print("    Editing & deleting files (2/3)")
    for file in csv_files:
        with open(file, 'r') as csv_file:
            rows = csv.reader(csv_file)
            modified_rows = []
            for row in rows:
                if row:
                    modified_row = [row[0], *row[4:6]]
                    modified_row[2] = modified_row[2].replace('Cr', '')
                    if int(modified_row[1]) >= 20000:
                        modified_rows.append(modified_row)
        with open(file, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(modified_rows)
        if os.stat(file).st_size == 0:
            os.remove(file)
            print(f"    -      {os.path.splitext(file)[0].replace('Export','')} removed due to insufficient demand")
    print("    All files edited (3/3)")
def DeleteNonMatchingFiles():
    print("    Indexing all files (1/3)")
    import_files = [file for file in os.listdir('.') if file.endswith('Import.csv')]
    export_files = [file for file in os.listdir('.') if file.endswith('Export.csv')]
    print("    Comparing files and deleting non-matching files (2/3)")
    print("    -    Managing import files (1/2)")
    for import_file in import_files:
        term = os.path.splitext(import_file)[0]
        term = term.replace("Import","")
        export_file = f"{term}Export.csv"
        if export_file not in export_files:
            print(f"    -    -    {os.path.splitext(import_file)[0].replace('Import','')} removed due to no export file counterpart")
            os.remove(import_file)
    print("    -    Managing export files (2/2)")
    for export_file in export_files:
        term = os.path.splitext(export_file)[0]
        term = term.replace("Export","")
        import_file = f"{term}Import.csv"

        if import_file not in import_files:
            print(f"    -    -    {os.path.splitext(export_file)[0].replace('Export','')} removed due to no import file counterpart")
            os.remove(export_file)
    print("    Non-matching files deleted (3/3)")
def SortProfit():
    print("    Compiling list of files to sort (1/4)")
    csv_files = [file for file in os.listdir('.') if file.endswith('Import.csv')]
    print("    Editing & sorting import files (2/4)")
    for csv_file in csv_files:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            data = [row for row in data if '-' not in row[2]]
            for row in data:
                first_variable = row[0].split("|")
                row.append(first_variable[0])
                row.append(first_variable[1])
                row.pop(0)
            sorted_data = sorted(data, key=lambda row: int(row[1]), reverse=False)
            output_file = csv_file
            with open(output_file, 'w', newline='') as output_file:
                writer = csv.writer(output_file)
                for row in sorted_data[:5]:
                    writer.writerow(row)
        csv_files = [file for file in os.listdir('.') if file.endswith('Export.csv')]
    print("    Editing & sorting export files (3/4)")
    for csv_file in csv_files:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            data = [row for row in data if '-' not in row[2]]
            for row in data:
                first_variable = row[0].split("|")
                row.append(first_variable[0])
                row.append(first_variable[1])
                row.pop(0)
            sorted_data = sorted(data, key=lambda row: int(row[1]), reverse=True)
            output_file = csv_file
            with open(output_file, 'w', newline='') as output_file:
                writer = csv.writer(output_file)
                for row in sorted_data[:5]:
                    writer.writerow(row)
    print("    Finished editing files (4/4)")
def ProfitValidation():
    print("    Compiling list of routes to sort (1/3)")
    files = [file for file in os.listdir('.') if file.endswith('Import.csv') or file.endswith('Export.csv')]
    print("    Verifying each route's profitability & removing unprofitable routes (2/3)")
    for file in files:
        file_prefix = file.replace('Import.csv', '').replace('Export.csv', '')
        with open(f"{file_prefix}Import.csv", 'r') as import_file:
            reader = csv.reader(import_file)
            import_rows = list(reader)
            MaxImportRow = import_rows[0]
            MaxImport = MaxImportRow[1]
        with open(f"{file_prefix}Export.csv", 'r') as export_file:
            reader = csv.reader(export_file)
            export_rows = list(reader)
            MaxExportRow = export_rows[0]
            MaxExport = MaxExportRow[1]
        if int(MaxExport) - int(MaxImport) < 338:
            print(f"    -    {file_prefix} was removed as it is unprofitable")
            os.remove(f"{file_prefix}Export.csv")
            os.remove(f"{file_prefix}Import.csv")
            files.remove(f"{file_prefix}Import.csv")
            files.remove(f"{file_prefix}Export.csv")
    print("    Unprofitable routes removed (3/3)")
def SystemCoordinates(system):
    star = system.replace("+", "%2B")
    coordinates = CheckSystemCoords(system)
    if coordinates is not None:
        return coordinates
    response = requests.get(f'https://www.edsm.net/api-v1/system?showCoordinates=1&systemName={star}')
    data = response.json()
    if 'coords' in data:
        SaveSystemCoords(system, data['coords'])
        print(f"    -    New system: {system} - Coordinates Saved")
        return data['coords']
    else:
        print(f"    -    Error with {system}")
        return None
def CheckSystemCoords(system):
    with open('!Coordinates.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == system:
                return {'x': row[1], 'y': row[2], 'z': row[3]}
    return None
def SaveSystemCoords(system, coords):
    with open('!Coordinates.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([system, coords['x'], coords['y'], coords['z']])
def SystemDistance(System1, System2):
    x_difference = float(System2["x"]) - float(System1["x"])
    y_difference = float(System2["y"]) - float(System1["y"])
    z_difference = float(System2["z"]) - float(System1["z"])
    return math.sqrt(x_difference**2 + y_difference**2 + z_difference**2)
def MaximisingProfit():
    with open("!Profit.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow("")
    print("    Compiling list of routes to sort (1/3)")
    ImportFiles = [file for file in os.listdir('.') if file.endswith('Import.csv')]
    print("    Maximising each route's profitability (2/3)")
    for file in ImportFiles:
        file_prefix = file.replace('Import.csv', '')
        HighestProfit = float('-inf')
        highest_import_row = None
        highest_export_row = None
        with open(f"{file_prefix}Import.csv", 'r') as import_file:
            import_reader = csv.reader(import_file)
            import_rows = list(import_reader)
            for import_row in import_rows:
                ImportSystem = import_row[3]
                ImportCost = import_row[1]
                with open(f"{file_prefix}Export.csv", 'r') as export_file:
                    export_reader = csv.reader(export_file)
                    export_rows = list(export_reader)
                    for export_row in export_rows:
                        ExportSystem = export_row[3]
                        ExportCost = export_row[1]
                        TotalProfit = (int(ExportCost) - int(ImportCost)) * 20000
                        Distance = SystemDistance(SystemCoordinates(ImportSystem), SystemCoordinates(ExportSystem))
                        FuelUsed = round((0.00000985*25000+0.26309)*Distance+10)
                        JumpCost = math.ceil(Distance / 500) * 100000 + math.ceil(Distance / 500) * FuelUsed * 50000
                        FinalProfit = TotalProfit - JumpCost
                        if FinalProfit > HighestProfit:
                            HighestProfit = FinalProfit
                            highest_import_row = import_row
                            highest_export_row = export_row
                            HighestExportDistance = round(Distance, 2)
        HighestExport = highest_export_row.pop(0)
        HighestImport = highest_import_row.pop(0)
        with open("!Profit.csv", 'a', newline='') as profit_file:
            profit_writer = csv.writer(profit_file)
            profit_writer.writerow([file_prefix] + [HighestProfit] + highest_import_row + highest_export_row + [HighestExportDistance])
        os.remove(f"{file_prefix}Import.csv")
        os.remove(f"{file_prefix}Export.csv")
    print("    Removing less profitable routes (3/5)")
    with open('!Profit.csv', 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)
        rows = rows[1:]
        filtered_data = [row for row in rows if float(row[1]) > 100000000]
    print("    Sorting the commodities (4/5)")
    sorted_data = sorted(filtered_data, key=lambda x: float(x[1]), reverse=True)
    with open('!Profit.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(sorted_data)
    print("    All routes sorted (5/5)")
def FormatRoutes():
    print("    Wiping old routes (1/5)")
    with open('MostProfitableRoutes.txt', 'w') as file:
        file.write("")
        print("    Getting all routes to format (2/5)")
    with open('!Profit.csv', 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        print("    Formatting routes (3/5)")
        with open('MostProfitableRoutes.txt', 'a') as file:
            now = datetime.datetime.now()
            RightNow = now.strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"Last update: {RightNow}\n")
            for row in data:
                formatted_route = f"""
    Commodity: {row[0]}
    Estimated Profit (20,000T): {int(row[1]):,} CR
    System to buy {row[0]}: {row[4]}
    Station to buy {row[0]}: {row[3]}
    Price per ton: {int(row[2]):,} CR
    System to sell {row[0]}: {row[7]}
    Station to sell {row[0]}: {row[6]}
    Price per ton: {int(row[5]):,} CR
    Distance: {(row[8])} LY\n"""
                file.write(formatted_route)
            print("Saving all routes to 'MostProfitableRoutes.txt' (4/5)")
    print("    All routes saved (5/5)")
print("Verifying commodity list (1/11)")
ListMaker()
print("Grabbing import commodity data (2/11)")
ImportCommodityData()
print("Editing import commodity data (3/11)")
EditImCommodityData()
print("Grabbing export commodity data (4/11)")
ExportCommodityData()
print("Editing export commodity data (5/11)")
EditExCommodityData()
print("Deleting non-matching files (6/11)")
DeleteNonMatchingFiles()
print("Sorting Rows (7/11)")
SortProfit()
print("Disregarding unprofitable routes (8/11)")
ProfitValidation()
print("Finding maximum profit for each commodity (9/11)")
MaximisingProfit()
print("Formatting routes (10/11)")
FormatRoutes()
print("All routes formatted (11/11)")
with open('!Profit.csv', 'r') as file:
    reader = csv.reader(file)
    data = list(reader)
    MostProfit = data [0]
print(f"""
The most profitable commodity at the moment is {MostProfit[0]} with an expected profit of {int(MostProfit[1]):,} credits if you buy 20,000 Tons.
You can buy this for the lowest price ({int(MostProfit[2]):,} credits) at {MostProfit[3]} in the {MostProfit[4]} system.
You can then sell this for the highest price ({int(MostProfit[5]):,} credits) at {MostProfit[6]} in the {MostProfit[7]} system.
The distance between both systems is {MostProfit[8]} light years.
Other very profitable routes can be found in the file titled 'MostProfitableRoutes.txt' in the same folder as this script.""")
os.remove('!Profit.csv')
