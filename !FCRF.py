import requests, csv, os, math, json, datetime, urllib.parse
from bs4 import BeautifulSoup
def SystemCoordinates(system):
    star = system.replace("+", "%2B")
    coordinates = CheckSystemCoords(system)
    if coordinates is not None:
        return coordinates
    response = requests.get(f'https://www.edsm.net/api-v1/system?showCoordinates=1&systemName={star}')
    data = response.json()
    if 'coords' in data:
        SaveSystemCoords(system, data['coords'])
        print(f"    === Coordinates Saved: {system}")
        return data['coords']
    else:
        print(f"    === Error with {system}")
        return None
def CheckSystemCoords(system):
    with open('Coordinates.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0]   == system:
                return {'x': row[1], 'y': row[2], 'z': row[3]}
    return None
def SaveSystemCoords(system, coords):
    with open('Coordinates.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([system, coords['x'], coords['y'], coords['z']])
def SystemDistance(System1, System2):
    x_difference = float(System2["x"]) - float(System1["x"])
    y_difference = float(System2["y"]) - float(System1["y"])
    z_difference = float(System2["z"]) - float(System1["z"])
    return math.sqrt(x_difference**2 + y_difference**2 + z_difference**2)
def ListMaker():
    url = 'https://inara.cz/elite/commodities-list/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')
    numbers = []
    for row in rows:
        link_element = row.find('a')
        if link_element is not None:
            link = link_element['href']
            number = link.replace("/elite/commodity/", '').replace("/", '')
            cells = row.find_all('td')
            try:
                cell_texts = [cell.get_text(strip=True).replace(',', '') for cell in cells]
                if all(cell_texts) and all(int(value.replace('Cr', '')) != 0 for value in cell_texts[1:3]):
                    numbers.append(number)
            except IndexError:
                continue
    print(f"Found {len(numbers)} eligible commodities")
    return numbers
def VerifyCommodity(number):
    ImportLink = f"https://inara.cz/elite/commodities/?pi1=1&pa1%5B%5D={number}&ps1=Sol&pi10=2&pi11=0&pi3=1&pi9=0&pi4=2&pi5=720&pi12=0&pi7=0&pi8=1"
    Iresponse = requests.get(ImportLink)
    Isoup = BeautifulSoup(Iresponse.content, 'html.parser')
    option_element = Isoup.find('option', attrs={'value': str(number), 'selected': True})
    if option_element is not None:
        term = option_element.get_text(strip=True)
    ImportTable = Isoup.find('table')
    if ImportTable is None:
        print(f"    ======= Insufficient import locations found for {term}, skipping to the next commodity")
        return None
    ImportRows = ImportTable.find_all('tr')
    SecondImportRows = []
    SecondExportRows = []
    for row in ImportRows[1:]:
        cells = row.find_all('td')
        ImportCells = [cell.get_text(strip=True).replace(',', '').replace('\uFFFD', "").replace("PP+",'').replace('\ue84d', "").replace("\ue81d",'').replace("\ufe0e",'').replace("︎",'').replace('\ue84f', "").replace('\ue81d', "").replace('\ue84e', "").replace('\ue823', '') for cell in cells]
        modified_row = [ImportCells[0], *ImportCells[4:6]]
        modified_row[2] = modified_row[2].replace('Cr', '')
        if int(modified_row[1]) >= 20000:
            SecondImportRows.append(modified_row)
    if SecondImportRows   == []:
        print(f"    ======= Insufficient stock for {term}, skipping to the next commodity")
        return None
    ExportLink = f"https://inara.cz/elite/commodities/?pi1=2&pa1%5B%5D={number}&ps1=Sol&pi10=2&pi11=0&pi3=1&pi9=0&pi4=2&pi5=720&pi12=0&pi7=0&pi8=1"
    Eresponse = requests.get(ExportLink)
    Esoup = BeautifulSoup(Eresponse.content, 'html.parser')
    ExportTable = Esoup.find('table')
    if ExportTable is None:
        print(f"    ======= Insufficient export locations for {term}, skipping to the next commodity")
        return None
    ExportRows = ExportTable.find_all('tr')
    for row in ExportRows[1:]:
        cells = row.find_all('td')
        for cell in cells:
            ExportCells = [cell.get_text(strip=True).replace(',', '').replace("PP+",'').replace('\uFFFD', "").replace('\ue84d', "").replace("\ue81d",'').replace("\ufe0e",'').replace("︎",'').replace('\ue84f', "").replace('\ue81d', "").replace('\ue84e', "").replace('\ue823', '') for cell in cells]
        modified_row = [ExportCells[0], *ExportCells[4:6]]
        modified_row[2] = modified_row[2].replace('Cr', '')
        if int(modified_row[1]) >= 20000:
            SecondExportRows.append(modified_row)
    if SecondExportRows == []:
        print(f"    ======= Insufficient demand for {term}, skipping to next commodity")
        return None
    for row in SecondImportRows:
        first_variable = row[0].split("|")
        row.append(first_variable[0])
        row.append(first_variable[1])
        row.pop(0)
    for row in SecondExportRows:
        first_variable = row[0].split("|")
        row.append(first_variable[0])
        row.append(first_variable[1])
        row.pop(0)
    SecondImportRows = [row for row in SecondImportRows if '-' not in row[1]]
    SecondExportRows = [row for row in SecondExportRows if '-' not in row[1]]
    SortedImportRows = sorted(SecondImportRows, key=lambda row: int(row[1]), reverse=False)
    SortedExportRows = sorted(SecondExportRows, key=lambda row: int(row[1]), reverse=True)
    MaxImportRow = SortedImportRows[0]
    MaxImport = MaxImportRow[1]
    MaxExportRow = SortedExportRows[0]
    MaxExport = MaxExportRow[1]
    if int(MaxExport) - int(MaxImport) < 338:
        print(f"    ======= Insufficient profit for {term}, skipping to next commodity")
        return None
    ThirdImportRows = SortedImportRows[:5]
    ThirdExportRows = SortedExportRows[:5]
    HighestProfit = float('-inf')
    highest_import_row = None
    highest_export_row = None
    for ImportRow in ThirdImportRows:
        ImportSystem = ImportRow[3]
        ImportCost = ImportRow[1]
        for ExportRow in ThirdExportRows:
            ExportSystem = ExportRow[3]
            ExportCost = ExportRow[1]
            TotalProfit = (int(ExportCost) - int(ImportCost)) * 20000
            Distance = SystemDistance(SystemCoordinates(ImportSystem), SystemCoordinates(ExportSystem))
            FuelUsed = round((0.00000985*25000+0.26309)*Distance+10)
            JumpCost = math.ceil(Distance / 500) * 100000 + math.ceil(Distance / 500) * FuelUsed * 50000
            FinalProfit = TotalProfit - JumpCost
            if FinalProfit > HighestProfit:
                HighestProfit = FinalProfit
                highest_import_row = ImportRow
                highest_export_row = ExportRow
                HighestProfitDistance = round(Distance, 2)
    HighestExportStation = highest_export_row[2]
    HighestImportStation = highest_import_row[2]
    HighestExportSystem = highest_export_row[3]
    HighestImportSystem = highest_import_row[3]
    highest_import_row.pop(0)
    highest_export_row.pop(0)
    if HighestProfit < 100000000:
        print(f"    ======= Insufficient total profit for {term}, skipping to next commodity")
        return None
    ExportPlanetFinderLink = f"https://www.edsm.net/en/search/stations/index/cmdrPosition/{HighestExportSystem}/name/{HighestExportStation}/sortBy/distanceCMDR"
    ImportPlanetFinderLink = f"https://www.edsm.net/en/search/stations/index/cmdrPosition/{HighestImportSystem}/name/{HighestImportStation}/sortBy/distanceCMDR"
    EPresponse = requests.get(ExportPlanetFinderLink)
    EPsoup = BeautifulSoup(EPresponse.content, 'html.parser')
    EPTable = EPsoup.find('tbody')
    if EPTable is None:
        print(f"    ================================ ERROR finding the station that buys {term} on EDSM - Station: {HighestExportStation} - {HighestExportSystem}, skipping to the next commodity")
        return None
    EStationLink = EPTable.find('a')['href']
    EStationLink = "https://www.edsm.net/"+EStationLink
    IPresponse = requests.get(ImportPlanetFinderLink)
    IPsoup = BeautifulSoup(IPresponse.content, 'html.parser')
    IPTable = IPsoup.find('tbody')
    if IPTable is None:
        print(f"    ================================ ERROR finding the station that sells {term} on EDSM - Station: {HighestExportStation} - {HighestExportSystem}, skipping to the next commodity")
        return None
    IStationLink = IPTable.find('a')['href']
    IStationLink = "https://www.edsm.net/"+IStationLink
    ESresponse = requests.get(EStationLink)
    ESsoup = BeautifulSoup(ESresponse.content, 'html.parser')
    EStationType = str(ESsoup.find_all('div', class_='col-lg-8')[1])
    EStationType = EStationType.replace('<div class="col-lg-8">','').replace('<strong class="scramble">','').replace('</strong>','').replace('</div>','').strip()
    EInfoType = str(ESsoup.find_all('div', class_='col-lg-4')[2])
    if "Distance to arrival:" in EInfoType:
        EStationDistance = str(ESsoup.find_all('div', class_='col-lg-8')[2])
        EStationDistance = EStationDistance.replace('<div class="col-lg-8">',"").replace('<strong>','').replace('</strong>','').replace("</div>",'').replace("ls",'').strip()
        EPlanet = "N/A"
    elif "Celestial body:" in EInfoType:
        EStationDistance = str(ESsoup.find_all('div', class_='col-lg-8')[2])
        EStationDistance = EStationDistance.replace('<div class="col-lg-8">',"").replace('<strong>','').replace('</strong>','').replace("</div>",'').replace("ls",'').strip()
        ESDsoup = BeautifulSoup(EStationDistance, 'html.parser')
        ESDTag = ESDsoup.find('em')
        EStationDistance = str(ESDTag.get_text(strip=True)).replace("(","").replace(")",'').strip()
        ESDATag = ESDsoup.find('a')
        EPlanet = str(ESDATag.get_text(strip=True)).replace(f"({EStationDistance})","").strip()
    else:
        EStationDistance = "N/A"
        EPlanet = "N/A"
    ISresponse = requests.get(IStationLink)
    ISsoup = BeautifulSoup(ISresponse.content, 'html.parser')
    IStationType = str(ISsoup.find_all('div', class_='col-lg-8')[1])
    IStationType = IStationType.replace('<div class="col-lg-8">','').replace('<strong class="scramble">','').replace('</strong>','').replace('</div>','').strip()
    IInfoType = str(ISsoup.find_all('div', class_='col-lg-4')[2])
    if "Distance to arrival:" in IInfoType:
        IStationDistance = str(ISsoup.find_all('div', class_='col-lg-8')[2])
        IStationDistance = IStationDistance.replace('<div class="col-lg-8">',"").replace('<strong>','').replace('</strong>','').replace("</div>",'').replace("ls",'').strip()
        IPlanet = "N/A"
    elif "Celestial body:" in IInfoType:
        IStationDistance = str(ISsoup.find_all('div', class_='col-lg-8')[2])
        IStationDistance = IStationDistance.replace('<div class="col-lg-8">',"").replace('<strong>','').replace('</strong>','').replace("</div>",'').replace("ls",'').strip()
        ISDsoup = BeautifulSoup(IStationDistance, 'html.parser')
        ISDTag = ISDsoup.find('em')
        IStationDistance = str(ISDTag.get_text(strip=True)).replace("(","").replace(")",'').strip()
        ISDATag = ISDsoup.find('a')
        IPlanet = str(ISDATag.get_text(strip=True)).replace(f"({IStationDistance})","").strip()
    else:
        IStationDistance = "N/A"
        IPlanet = "N/A"
    print(f"    ================ {term} fulfilled every requirement, continuing to next commodity")
    return [[term] + [HighestProfit] + highest_import_row + highest_export_row + [HighestProfitDistance] + [IStationType] + [IStationDistance] + [IPlanet] + [EStationType] + [EStationDistance] + [EPlanet]]
def SortCommodities():
    ViableCommodities = []
    with open('MostProfitableRoutes.txt', 'w') as file:
            file.write("")
    numbers = ListMaker()
    for number in numbers:
        Commodity = VerifyCommodity(number)
        if Commodity is not None:
            TCommodity = Commodity[0]
            ViableCommodities.append(TCommodity)
    OrganizedCommodities = sorted(ViableCommodities, key=lambda x: float(x[1]), reverse=True)
    with open('MostProfitableRoutes.txt', 'a') as file:
        now = datetime.datetime.now()
        RightNow = now.strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"Last update: {RightNow}\n")
        for row in OrganizedCommodities:
            formatted_route = f"""
Commodity: {row[0]}
    Estimated Profit (20,000T): {int(row[1]):,} CR

    System to buy {row[0]}: {row[4]}
    Station to buy {row[0]}: {row[3]}
    Distance from star: {row[10]} LS
    Station type: {row[9]}
    Station orbits/is located on: {row[11]}
    Price per ton: {int(row[2]):,} CR

    System to sell {row[0]}: {row[7]}
    Station to sell {row[0]}: {row[6]}
    Distance from star: {row[13]} LS
    Station type: {row[12]}
    Station orbits/is located on: {row[14]}
    Price per ton: {int(row[5]):,} CR

    Distance: {(row[8])} LY\n"""
            file.write(formatted_route)
    MostProfit = OrganizedCommodities[0]
    print(f"""
The most profitable commodity at the moment is {MostProfit[0]} with an expected profit of {int(MostProfit[1]):,} credits if you buy 20,000 Tons.
You can buy this for the lowest price ({int(MostProfit[2]):,} credits) at {MostProfit[3]} in the {MostProfit[4]} system. {MostProfit[3]} is a {MostProfit[9]} that orbits/is located on {MostProfit[11]} and is {MostProfit[10]} light seconds away from the star.
You can then sell this for the highest price ({int(MostProfit[5]):,} credits) at {MostProfit[6]} in the {MostProfit[7]} system. {MostProfit[6]} is a {MostProfit[12]} that orbits/is located on {MostProfit[14]} and is {MostProfit[13]} light seconds away from the star.
The distance between both systems is {MostProfit[8]} light years.
{len(ViableCommodities)-1} other very profitable routes can be found in the file titled 'MostProfitableRoutes.txt' in the same folder as this script.""")
SortCommodities()
