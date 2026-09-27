"""Hand-made map of matching chapters across editions of the same series.

SERIES[series] = {"books": [...slugs in date order], "topics": {topic: {slug: [chapter names as printed in data/<slug>.json]}}}
A chapter may sit under more than one topic (e.g. 1905 "Justice, Police and Sanitation").
Topics present in only one edition are left out.
"""

SERIES = {
    "japan": {
        "name": "The Japan Year Book",
        "books": ["japan-1905", "japan-1910", "japan-1920-21", "japan-1930", "japan-1935", "japan-1939-40", "japan-1946-48"],
        "topics": {
            "Weights, Measures and Moneys": {
                "japan-1905": ["Weights, Measures and Moneys"], "japan-1910": ["Weights, Measures and Moneys"],
                "japan-1920-21": ["Weights, Measures and Moneys"], "japan-1930": ["Weights, Measures and Moneys"],
                "japan-1935": ["Weights and Measures"], "japan-1939-40": ["Japanese Weights and Measures"]},
            "Geography": {
                "japan-1905": ["Geography"], "japan-1910": ["Geography"], "japan-1920-21": ["Geography"],
                "japan-1930": ["Geography"], "japan-1935": ["Geography"], "japan-1939-40": ["Geography"],
                "japan-1946-48": ["Geography"]},
            "Earthquakes, Volcanoes and Mineral Springs": {
                "japan-1910": ["Earthquakes, Volcanoes and Mineral Springs"],
                "japan-1920-21": ["Earthquakes, Volcanoes and Mineral Springs"],
                "japan-1930": ["Geology, Volcanoes and Mineral Springs", "Earthquakes in Japan"]},
            "History": {
                "japan-1920-21": ["Outline of Japanese History"], "japan-1939-40": ["Outline of History"],
                "japan-1946-48": ["Outline of the Cultural History"]},
            "Population": {
                "japan-1905": ["Population"], "japan-1910": ["Population"], "japan-1920-21": ["Population"],
                "japan-1930": ["Population and Emigration"], "japan-1935": ["Population"],
                "japan-1939-40": ["Population"], "japan-1946-48": ["Population"]},
            "Imperial Court": {
                "japan-1905": ["Imperial Court"], "japan-1910": ["Imperial Court"], "japan-1920-21": ["Imperial Court"],
                "japan-1930": ["Imperial Court"], "japan-1935": ["The Imperial Court"],
                "japan-1939-40": ["The Imperial Court"], "japan-1946-48": ["Imperial Court"]},
            "Government and Politics": {
                "japan-1905": ["Politics"], "japan-1910": ["Politics"], "japan-1920-21": ["Politics"],
                "japan-1930": ["Politics and Local Government"], "japan-1935": ["Government", "Parties and Politics"],
                "japan-1939-40": ["Government", "Parties and Politics"],
                "japan-1946-48": ["Government", "Parties and Politics"]},
            "Local Government": {
                "japan-1905": ["Local Administration"], "japan-1910": ["Local Administration"],
                "japan-1920-21": ["Local Government"], "japan-1930": ["Politics and Local Government"]},
            "Civil and Military Service": {
                "japan-1920-21": ["Civil and Military Service"], "japan-1930": ["Civil and Military Service"]},
            "Diplomacy and Foreign Relations": {
                "japan-1905": ["Diplomacy and Dip'tic and Consular Services"],
                "japan-1910": ["Diplomacy and Diplomatic Service"], "japan-1920-21": ["Diplomacy"],
                "japan-1930": ["Diplomacy"], "japan-1935": ["Foreign Relations"], "japan-1939-40": ["Foreign Relations"]},
            "Army, Navy and National Defence": {
                "japan-1905": ["Army and the Navy"], "japan-1910": ["Army and the Navy"],
                "japan-1920-21": ["The Army, Navy and Aviation"], "japan-1930": ["National Defence"],
                "japan-1935": ["National Defence"], "japan-1939-40": ["National Defence"]},
            "Finance": {
                "japan-1905": ["Finances", "War Finance"], "japan-1910": ["Finances"], "japan-1920-21": ["Finance"],
                "japan-1930": ["Finance"], "japan-1935": ["Public Finance"], "japan-1939-40": ["Public Finance"],
                "japan-1946-48": ["Public Finance"]},
            "Banking": {
                "japan-1905": ["Banks and Banking Business"], "japan-1910": ["Banks and Banking Business"],
                "japan-1920-21": ["Banks and Banking Business"], "japan-1930": ["Banks and Banking Business"],
                "japan-1935": ["Banking and the Money Market"], "japan-1939-40": ["Banking and the Money Market"],
                "japan-1946-48": ["Banking and Money Market"]},
            "Insurance": {
                "japan-1920-21": ["Insurance"], "japan-1930": ["Insurance"], "japan-1935": ["Insurance"],
                "japan-1939-40": ["Insurance"], "japan-1946-48": ["Insurance"]},
            "Agriculture": {
                "japan-1905": ["Agriculture"], "japan-1910": ["Agriculture"], "japan-1920-21": ["Agriculture"],
                "japan-1930": ["Agriculture"], "japan-1935": ["Agriculture"], "japan-1939-40": ["Agriculture"],
                "japan-1946-48": ["Agriculture"]},
            "Sericulture and Raw Silk": {
                "japan-1930": ["Sericulture"], "japan-1935": ["Sericulture and Raw Silk"],
                "japan-1939-40": ["Sericulture and Raw Silk"], "japan-1946-48": ["Sericulture and Raw Silk"]},
            "Forestry": {
                "japan-1905": ["Forestry and Fishery"], "japan-1910": ["Forestry"], "japan-1920-21": ["Forestry"],
                "japan-1930": ["Forestry"], "japan-1935": ["Forestry"], "japan-1939-40": ["Forestry"],
                "japan-1946-48": ["Forestry"]},
            "Fisheries": {
                "japan-1905": ["Forestry and Fishery"], "japan-1910": ["Fishery"], "japan-1920-21": ["Fishery"],
                "japan-1930": ["Fishery"], "japan-1935": ["Fisheries"], "japan-1939-40": ["Fisheries"],
                "japan-1946-48": ["Fisheries"]},
            "Mining": {
                "japan-1905": ["Mines and Mining"], "japan-1910": ["Mines and Mining"],
                "japan-1920-21": ["Mines and Mining"], "japan-1930": ["Mines and Mining"], "japan-1935": ["Mining"],
                "japan-1939-40": ["Mining"], "japan-1946-48": ["Mining"]},
            "Industry": {
                "japan-1905": ["Manufacturing Industry"], "japan-1910": ["Industry"], "japan-1920-21": ["Industry"],
                "japan-1930": ["Industry"],
                "japan-1935": ["The Textile Industry", "Machinery and Engineering", "Miscellaneous Industries",
                               "Miscellaneous Industries (Continued)"],
                "japan-1939-40": ["The Textile Industry", "Machinery and Engineering", "Foodstuffs (Manufactured)",
                                  "Chemical Industry", "Miscellaneous Industries"],
                "japan-1946-48": ["Textile Industry", "Chemical Industry", "Miscellaneous Industries"]},
            "Public Utilities": {
                "japan-1939-40": ["Utilities"], "japan-1946-48": ["Public Utilities"]},
            "Patents, Designs and Trade-Marks": {
                "japan-1905": ["Patents, Designs and Trade Marks"], "japan-1910": ["Patents, Trade-marks and Designs"],
                "japan-1920-21": ["Patents, Designs, Trade-Marks and Utility Models"]},
            "Home Trade and Commerce": {
                "japan-1905": ["Mercantile Establishments"], "japan-1910": ["Home Trade", "Economic Corporations"],
                "japan-1920-21": ["Trade"], "japan-1930": ["Trade"], "japan-1935": ["Home Trade and Commerce"],
                "japan-1939-40": ["Commerce and Industry"]},
            "Foreign Trade": {
                "japan-1905": ["Foreign Trade"], "japan-1910": ["Foreign Trade"], "japan-1920-21": ["Foreign Trade"],
                "japan-1930": ["Foreign Trade"], "japan-1935": ["Foreign Trade"], "japan-1939-40": ["Foreign Trade"],
                "japan-1946-48": ["Foreign Trade"]},
            "Communications (Post, Telegraph, Telephone)": {
                "japan-1905": ["Communications", "Communications (Post, Telegraph and Telephone)"],
                "japan-1910": ["Communications"], "japan-1920-21": ["Communications"],
                "japan-1930": ["Post, Telegraph & Telephone"], "japan-1939-40": ["Communications"],
                "japan-1946-48": ["Communications"]},
            "Railways and Land Transport": {
                "japan-1905": ["Railways"], "japan-1910": ["Railways"], "japan-1920-21": ["Railways"],
                "japan-1930": ["Railways"], "japan-1939-40": ["Land and Air Transportation"],
                "japan-1946-48": ["Transportation"]},
            "Shipping and Shipbuilding": {
                "japan-1905": ["Mercantile Marine"], "japan-1910": ["Mercantile Marine"],
                "japan-1920-21": ["Mercantile Marine & Shipbuilding Industry"], "japan-1930": ["Shipping and Shipbuilding"],
                "japan-1939-40": ["Sea Transportation"], "japan-1946-48": ["Transportation"]},
            "Public Works and Construction": {
                "japan-1910": ["Construction & Public Works"], "japan-1920-21": ["Public Works"],
                "japan-1930": ["Construction"]},
            "Education": {
                "japan-1905": ["Education"], "japan-1910": ["Education"], "japan-1920-21": ["Education"],
                "japan-1930": ["Education"], "japan-1939-40": ["Education"], "japan-1946-48": ["Education"]},
            "Religion": {
                "japan-1905": ["Religions"], "japan-1910": ["Religions and Religious Works"],
                "japan-1920-21": ["Religions and Religious Work"], "japan-1930": ["Religion and Religious Works"],
                "japan-1939-40": ["Religion"], "japan-1946-48": ["Religion"]},
            "Justice, Police and Prisons": {
                "japan-1905": ["Justice, Police and Sanitation"], "japan-1910": ["Justice, Prisons, Police and Sanitation"],
                "japan-1920-21": ["Justice, Prisons, Police and Sanitation"], "japan-1930": ["Justice, Police and Prisons"],
                "japan-1939-40": ["Justice and Police"], "japan-1946-48": ["Justice and Police"]},
            "Medicine and Sanitation": {
                "japan-1905": ["Justice, Police and Sanitation"], "japan-1910": ["Justice, Prisons, Police and Sanitation"],
                "japan-1920-21": ["Justice, Prisons, Police and Sanitation"], "japan-1930": ["Medicine and Sanitation"],
                "japan-1939-40": ["Medicine and Sanitation"], "japan-1946-48": ["Medicine and Sanitation"]},
            "Charity, Relief and Social Work": {
                "japan-1910": ["Charity and Relief"], "japan-1920-21": ["Charity and Relief"],
                "japan-1930": ["Social Problems and Facts"], "japan-1939-40": ["Social Problems and Social Works"],
                "japan-1946-48": ["Social Work"]},
            "Labour": {
                "japan-1910": ["Social Politics & Labour Problems"], "japan-1920-21": ["Social Politics and Labor Problems"],
                "japan-1930": ["Labor"], "japan-1939-40": ["Labour and Labour Movements"],
                "japan-1946-48": ["Labor and Labor Movement"]},
            "Press and Publications": {
                "japan-1905": ["The Press"], "japan-1910": ["The Press"], "japan-1920-21": ["Press and Publication"],
                "japan-1930": ["Press and Publication"], "japan-1939-40": ["Press and Publications"],
                "japan-1946-48": ["Press and Publications"]},
            "Arts, Literature and Music": {
                "japan-1910": ["Arts and Crafts of Modern Japan"], "japan-1920-21": ["Arts and Crafts"],
                "japan-1930": ["Arts and Crafts"], "japan-1939-40": ["Literature, Arts and Music"],
                "japan-1946-48": ["Literature, Arts and Music"]},
            "Sports": {
                "japan-1920-21": ["Sports and Amusements", "Sports and Amusement"], "japan-1930": ["Sports"],
                "japan-1939-40": ["Sports"], "japan-1946-48": ["Sports"]},
            "Amusements": {
                "japan-1920-21": ["Sports and Amusements", "Sports and Amusement"], "japan-1930": ["Amusements"],
                "japan-1939-40": ["Amusements and Calendar of Annual Events"],
                "japan-1946-48": ["Amusements and Calendar of Annual Events"]},
            "Great Cities": {
                "japan-1930": ["Six Premier Cities"], "japan-1939-40": ["Tokyo", "Five Big Cities"]},
            "Korea (Chosen)": {
                "japan-1905": ["Korea"], "japan-1910": ["Korea"], "japan-1920-21": ["Chosen (Korea)"],
                "japan-1930": ["Chosen (Korea)"], "japan-1939-40": ["Chosen (Korea)", "Chosen"]},
            "Taiwan (Formosa)": {
                "japan-1905": ["Formosa"], "japan-1910": ["Formosa"], "japan-1920-21": ["Taiwan (Formosa)"],
                "japan-1930": ["Taiwan (Formosa)"], "japan-1939-40": ["Taiwan (Formosa)"]},
            "Karafuto (Saghalien)": {
                "japan-1910": ["Karafuto"], "japan-1920-21": ["Karafuto (Saghalien)"],
                "japan-1930": ["Karafuto (Saghalien, Southern Half Below 50°)"],
                "japan-1939-40": ["Karafuto (Saghalien)", "Karafuto"]},
            "South Manchuria and Manchoukuo": {
                "japan-1910": ["South Manchuria"], "japan-1920-21": ["South Manchuria, the South Sea Islands and Tsingtao"],
                "japan-1930": ["South Manchuria & South Sea Islands", "South Manchuria and the South Sea Islands"],
                "japan-1939-40": ["Manchoukuo"]},
            "South Sea Islands": {
                "japan-1920-21": ["South Manchuria, the South Sea Islands and Tsingtao"],
                "japan-1930": ["South Manchuria & South Sea Islands", "South Manchuria and the South Sea Islands"],
                "japan-1939-40": ["South Sea Islands under Japan's Mandate"]},
        },
    },
    "china": {
        "name": "The China Year Book",
        "books": ["china-1912", "china-1922", "china-1929-30", "china-1938"],
        "topics": {
            "Calendar": {"china-1912": ["Calendars"], "china-1938": ["Calendar"]},
            "General Information: Area and Population": {
                "china-1912": ["The Chinese Empire"], "china-1922": ["Area and Population of China", "Geography"],
                "china-1929-30": ["General Information"], "china-1938": ["General Information"]},
            "Fauna": {"china-1912": ["Fauna"], "china-1922": ["Fauna"]},
            "Climate and Meteorology": {
                "china-1912": ["Climate and Meteorology"], "china-1922": ["Climate & Meteorology"],
                "china-1938": ["The Climate of China"]},
            "People and Language": {"china-1912": ["People and Language"], "china-1922": ["People & Language"]},
            "Products and Agriculture": {
                "china-1912": ["Products"], "china-1922": ["Products"],
                "china-1929-30": ["Products—General, Pastoral and Agricultural"]},
            "Mines and Minerals": {
                "china-1912": ["Mines and Mining"], "china-1922": ["Mines and Minerals"],
                "china-1929-30": ["Mines and Minerals"], "china-1938": ["Mineral Industry"]},
            "Money, Currency and Banking": {
                "china-1912": ["Money, Weights and Measures"], "china-1922": ["Money, Weights & Measures", "Currency"],
                "china-1929-30": ["Currency, Banks, Weights and Measures"], "china-1938": ["Currency and Banking"]},
            "Manufactures and Industry": {
                "china-1912": ["Manufactures"], "china-1922": ["Manufactures"],
                "china-1938": ["Modern Chinese Industries"]},
            "Commerce": {
                "china-1912": ["Commerce"], "china-1922": ["Commerce"], "china-1929-30": ["Trade and Commerce"],
                "china-1938": ["The Foreign Trade of China"]},
            "Customs Revenue and Trade Statistics": {
                "china-1912": ["Trade Statistics", "Trade Statistics—Silk", "Trade Statistics—Tea",
                               "Trade Statistics—Bullion", "Trade Statistics—Bullion and Specie"],
                "china-1922": ["Customs Revenue and Trade Statistics"],
                "china-1929-30": ["Customs Revenue and Trade Returns"],
                "china-1938": ["Customs Revenue and Trade Statistics"]},
            "Customs Tariff": {
                "china-1922": ["The Chinese Customs Tariff"],
                "china-1929-30": ["Customs Import Tariff of the Republic of China"],
                "china-1938": ["Customs Import Tariff of the Republic of China"]},
            "Communications": {
                "china-1912": ["Communications", "The Chinese Imperial Post Office"], "china-1922": ["Communications"],
                "china-1929-30": ["Communications—Railways and Roads", "Communications—Posts, Telegraphs and Aviation"],
                "china-1938": ["Communications"]},
            "Government": {
                "china-1912": ["The Government", "Constitutional Reform"], "china-1922": ["The Chinese Government"],
                "china-1929-30": ["The Chinese Government", "The Kuomintang"],
                "china-1938": ["The Kuomintang and the Government"]},
            "Army and Navy": {
                "china-1912": ["Defence", "The Navy"], "china-1922": ["Defence"], "china-1929-30": ["Army and Navy"],
                "china-1938": ["Army and Navy"]},
            "Finance": {
                "china-1912": ["Finance"], "china-1922": ["Finance", "The New Consortium"],
                "china-1929-30": ["Finance"], "china-1938": ["Finance"]},
            "Shipping": {"china-1912": ["Shipping"], "china-1929-30": ["Shipping"], "china-1938": ["Shipping"]},
            "Education": {
                "china-1912": ["Education"], "china-1922": ["Education"], "china-1929-30": ["Education"],
                "china-1938": ["Education"]},
            "Religions": {
                "china-1912": ["Religions"], "china-1922": ["Religions"], "china-1929-30": ["Religions"],
                "china-1938": ["Religions"]},
            "Public Justice": {
                "china-1922": ["Public Justice"], "china-1929-30": ["Public Justice"], "china-1938": ["Public Justice"]},
            "River Conservancy and Harbours": {
                "china-1922": ["River Conservancy & Harbour Works"],
                "china-1929-30": ["River Conservancy and Harbour Works"], "china-1938": ["River Conservancy and Harbours"]},
            "Public Health": {
                "china-1929-30": ["Public Health and Medical Events during 1927 and 1928"],
                "china-1938": ["Public Health"]},
            "Labour": {"china-1929-30": ["Labour"], "china-1938": ["Labour"]},
            "Colonies, Leased Territories and Concessions": {
                "china-1929-30": ["Colonies, Leased Territories and Settlements"],
                "china-1938": ["Colonies, Leased Territories, Concessions, Etc.",
                               "Colonies, Leased Territories, Concessions, etc."]},
            "Greater China": {"china-1929-30": ["Greater China"], "china-1938": ["Greater China"]},
            "International Problems": {
                "china-1922": ["China's War & Post-War Problems"], "china-1929-30": ["China's International Problems"]},
            "Miscellaneous": {
                "china-1912": ["Miscellaneous"], "china-1922": ["Miscellaneous"], "china-1929-30": ["Miscellaneous"],
                "china-1938": ["Miscellaneous"]},
        },
    },
    "china-handbook": {
        "name": "China Handbook",
        "books": ["china-1937-43", "china-1950"],
        "topics": {
            "General Information": {
                "china-1937-43": ["Chapter I. General Information", "General Information"],
                "china-1950": ["General Information"]},
            "Government Structure": {"china-1937-43": ["Government Structure"], "china-1950": ["Government Structure"]},
            "Political Parties": {"china-1937-43": ["The Kuomintang"], "china-1950": ["Political Parties"]},
            "Public Finance": {"china-1937-43": ["Public Finance"], "china-1950": ["Public Finance"]},
            "Communications": {
                "china-1937-43": ["Communications"],
                "china-1950": ["Communications", "Postal Service and Tele-Communications"]},
            "Courts, Police and Prisons": {
                "china-1937-43": ["Courts and Prisons"], "china-1950": ["Judicial System and Police"]},
            "Military Affairs and Defence": {"china-1937-43": ["Military Affairs"], "china-1950": ["National Defense"]},
            "Education": {"china-1937-43": ["Education and Research"], "china-1950": ["Education"]},
            "Industry": {"china-1937-43": ["Industry and Labor"], "china-1950": ["Industry"]},
            "Labour": {"china-1937-43": ["Industry and Labor"], "china-1950": ["Labor"]},
            "Mineral Resources": {"china-1937-43": ["Mineral Resources"], "china-1950": ["Mineral Resources"]},
            "Money and Banking": {"china-1937-43": ["Money and Banking"], "china-1950": ["Banking"]},
            "Foreign Trade": {"china-1937-43": ["Foreign Trade"], "china-1950": ["Foreign Trade"]},
            "Agriculture": {
                "china-1937-43": ["Agricultural Economy"],
                "china-1950": ["Agriculture", "Food", "Forestry, Animal Husbandry and Fisheries", "Land"]},
            "Prices": {"china-1937-43": ["Price and Commodity Control"], "china-1950": ["Commodity Prices"]},
            "Public Health and Medicine": {
                "china-1937-43": ["Public Health and Medicine"], "china-1950": ["Public Health and Medicine"]},
            "The Press": {"china-1937-43": ["The Press"], "china-1950": ["The Press"]},
            "Relief": {"china-1937-43": ["Relief Activities"], "china-1950": ["Relief and Rehabilitation"]},
        },
    },
}
