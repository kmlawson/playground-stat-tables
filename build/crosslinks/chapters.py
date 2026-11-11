"""Hand-made map of matching chapters across editions of the same series.

SERIES[series] = {"books": [...slugs in date order], "topics": {topic: {slug: [chapter names as printed in data/<slug>.json]}}}
A chapter may sit under more than one topic (e.g. 1905 "Justice, Police and Sanitation").
Topics present in only one edition are left out.
"""

SERIES = {
    "japan": {
        "name": "The Japan Year Book",
        "books": [
            "japan-1905",
            "japan-1910",
            "japan-1920-21",
            "japan-1930",
            "japan-1935",
            "japan-1939-40",
            "japan-1946-48"
        ],
        "topics": {
            "Weights, Measures and Moneys": {
                "japan-1905": [
                    "Weights, Measures and Moneys"
                ],
                "japan-1910": [
                    "Weights, Measures and Moneys"
                ],
                "japan-1920-21": [
                    "Weights, Measures and Moneys"
                ],
                "japan-1930": [
                    "Weights, Measures and Moneys"
                ],
                "japan-1935": [
                    "Weights and Measures"
                ],
                "japan-1939-40": [
                    "Japanese Weights and Measures"
                ]
            },
            "Geography": {
                "japan-1905": [
                    "Geography"
                ],
                "japan-1910": [
                    "Geography"
                ],
                "japan-1920-21": [
                    "Geography"
                ],
                "japan-1930": [
                    "Geography"
                ],
                "japan-1935": [
                    "Geography"
                ],
                "japan-1939-40": [
                    "Geography"
                ],
                "japan-1946-48": [
                    "Geography"
                ]
            },
            "Earthquakes, Volcanoes and Mineral Springs": {
                "japan-1910": [
                    "Earthquakes, Volcanoes and Mineral Springs"
                ],
                "japan-1920-21": [
                    "Earthquakes, Volcanoes and Mineral Springs"
                ],
                "japan-1930": [
                    "Geology, Volcanoes and Mineral Springs",
                    "Earthquakes in Japan"
                ]
            },
            "History": {
                "japan-1920-21": [
                    "Outline of Japanese History"
                ],
                "japan-1939-40": [
                    "Outline of History"
                ],
                "japan-1946-48": [
                    "Outline of the Cultural History"
                ]
            },
            "Population": {
                "japan-1905": [
                    "Population"
                ],
                "japan-1910": [
                    "Population"
                ],
                "japan-1920-21": [
                    "Population"
                ],
                "japan-1930": [
                    "Population and Emigration"
                ],
                "japan-1935": [
                    "Population"
                ],
                "japan-1939-40": [
                    "Population"
                ],
                "japan-1946-48": [
                    "Population"
                ]
            },
            "Imperial Court": {
                "japan-1905": [
                    "Imperial Court"
                ],
                "japan-1910": [
                    "Imperial Court"
                ],
                "japan-1920-21": [
                    "Imperial Court"
                ],
                "japan-1930": [
                    "Imperial Court"
                ],
                "japan-1935": [
                    "The Imperial Court"
                ],
                "japan-1939-40": [
                    "The Imperial Court"
                ],
                "japan-1946-48": [
                    "Imperial Court"
                ]
            },
            "Government and Politics": {
                "japan-1905": [
                    "Politics"
                ],
                "japan-1910": [
                    "Politics"
                ],
                "japan-1920-21": [
                    "Politics"
                ],
                "japan-1930": [
                    "Politics and Local Government"
                ],
                "japan-1935": [
                    "Government",
                    "Parties and Politics"
                ],
                "japan-1939-40": [
                    "Government",
                    "Parties and Politics"
                ],
                "japan-1946-48": [
                    "Government",
                    "Parties and Politics"
                ]
            },
            "Local Government": {
                "japan-1905": [
                    "Local Administration"
                ],
                "japan-1910": [
                    "Local Administration"
                ],
                "japan-1920-21": [
                    "Local Government"
                ],
                "japan-1930": [
                    "Politics and Local Government"
                ]
            },
            "Civil and Military Service": {
                "japan-1920-21": [
                    "Civil and Military Service"
                ],
                "japan-1930": [
                    "Civil and Military Service"
                ]
            },
            "Diplomacy and Foreign Relations": {
                "japan-1905": [
                    "Diplomacy and Dip'tic and Consular Services"
                ],
                "japan-1910": [
                    "Diplomacy and Diplomatic Service"
                ],
                "japan-1920-21": [
                    "Diplomacy"
                ],
                "japan-1930": [
                    "Diplomacy"
                ],
                "japan-1935": [
                    "Foreign Relations"
                ],
                "japan-1939-40": [
                    "Foreign Relations"
                ]
            },
            "Army, Navy and National Defence": {
                "japan-1905": [
                    "Army and the Navy"
                ],
                "japan-1910": [
                    "Army and the Navy"
                ],
                "japan-1920-21": [
                    "The Army, Navy and Aviation"
                ],
                "japan-1930": [
                    "National Defence"
                ],
                "japan-1935": [
                    "National Defence"
                ],
                "japan-1939-40": [
                    "National Defence"
                ]
            },
            "Finance": {
                "japan-1905": [
                    "Finances",
                    "War Finance"
                ],
                "japan-1910": [
                    "Finances"
                ],
                "japan-1920-21": [
                    "Finance"
                ],
                "japan-1930": [
                    "Finance"
                ],
                "japan-1935": [
                    "Public Finance"
                ],
                "japan-1939-40": [
                    "Public Finance"
                ],
                "japan-1946-48": [
                    "Public Finance"
                ]
            },
            "Banking": {
                "japan-1905": [
                    "Banks and Banking Business"
                ],
                "japan-1910": [
                    "Banks and Banking Business"
                ],
                "japan-1920-21": [
                    "Banks and Banking Business"
                ],
                "japan-1930": [
                    "Banks and Banking Business"
                ],
                "japan-1935": [
                    "Banking and the Money Market"
                ],
                "japan-1939-40": [
                    "Banking and the Money Market"
                ],
                "japan-1946-48": [
                    "Banking and Money Market"
                ]
            },
            "Insurance": {
                "japan-1920-21": [
                    "Insurance"
                ],
                "japan-1930": [
                    "Insurance"
                ],
                "japan-1935": [
                    "Insurance"
                ],
                "japan-1939-40": [
                    "Insurance"
                ],
                "japan-1946-48": [
                    "Insurance"
                ]
            },
            "Agriculture": {
                "japan-1905": [
                    "Agriculture"
                ],
                "japan-1910": [
                    "Agriculture"
                ],
                "japan-1920-21": [
                    "Agriculture"
                ],
                "japan-1930": [
                    "Agriculture"
                ],
                "japan-1935": [
                    "Agriculture"
                ],
                "japan-1939-40": [
                    "Agriculture"
                ],
                "japan-1946-48": [
                    "Agriculture"
                ]
            },
            "Sericulture and Raw Silk": {
                "japan-1930": [
                    "Sericulture"
                ],
                "japan-1935": [
                    "Sericulture and Raw Silk"
                ],
                "japan-1939-40": [
                    "Sericulture and Raw Silk"
                ],
                "japan-1946-48": [
                    "Sericulture and Raw Silk"
                ]
            },
            "Forestry": {
                "japan-1905": [
                    "Forestry and Fishery"
                ],
                "japan-1910": [
                    "Forestry"
                ],
                "japan-1920-21": [
                    "Forestry"
                ],
                "japan-1930": [
                    "Forestry"
                ],
                "japan-1935": [
                    "Forestry"
                ],
                "japan-1939-40": [
                    "Forestry"
                ],
                "japan-1946-48": [
                    "Forestry"
                ]
            },
            "Fisheries": {
                "japan-1905": [
                    "Forestry and Fishery"
                ],
                "japan-1910": [
                    "Fishery"
                ],
                "japan-1920-21": [
                    "Fishery"
                ],
                "japan-1930": [
                    "Fishery"
                ],
                "japan-1935": [
                    "Fisheries"
                ],
                "japan-1939-40": [
                    "Fisheries"
                ],
                "japan-1946-48": [
                    "Fisheries"
                ]
            },
            "Mining": {
                "japan-1905": [
                    "Mines and Mining"
                ],
                "japan-1910": [
                    "Mines and Mining"
                ],
                "japan-1920-21": [
                    "Mines and Mining"
                ],
                "japan-1930": [
                    "Mines and Mining"
                ],
                "japan-1935": [
                    "Mining"
                ],
                "japan-1939-40": [
                    "Mining"
                ],
                "japan-1946-48": [
                    "Mining"
                ]
            },
            "Industry": {
                "japan-1905": [
                    "Manufacturing Industry"
                ],
                "japan-1910": [
                    "Industry"
                ],
                "japan-1920-21": [
                    "Industry"
                ],
                "japan-1930": [
                    "Industry"
                ],
                "japan-1935": [
                    "The Textile Industry",
                    "Machinery and Engineering",
                    "Miscellaneous Industries",
                    "Miscellaneous Industries (Continued)",
                    "Foodstuffs"
                ],
                "japan-1939-40": [
                    "The Textile Industry",
                    "Machinery and Engineering",
                    "Foodstuffs (Manufactured)",
                    "Chemical Industry",
                    "Miscellaneous Industries"
                ],
                "japan-1946-48": [
                    "Textile Industry",
                    "Chemical Industry",
                    "Miscellaneous Industries"
                ]
            },
            "Public Utilities": {
                "japan-1935": [
                    "Utilities"
                ],
                "japan-1939-40": [
                    "Utilities"
                ],
                "japan-1946-48": [
                    "Public Utilities"
                ]
            },
            "Patents, Designs and Trade-Marks": {
                "japan-1905": [
                    "Patents, Designs and Trade Marks"
                ],
                "japan-1910": [
                    "Patents, Trade-marks and Designs"
                ],
                "japan-1920-21": [
                    "Patents, Designs, Trade-Marks and Utility Models"
                ]
            },
            "Home Trade and Commerce": {
                "japan-1905": [
                    "Mercantile Establishments"
                ],
                "japan-1910": [
                    "Home Trade",
                    "Economic Corporations"
                ],
                "japan-1920-21": [
                    "Trade"
                ],
                "japan-1930": [
                    "Trade"
                ],
                "japan-1935": [
                    "Home Trade and Commerce"
                ],
                "japan-1939-40": [
                    "Commerce and Industry"
                ]
            },
            "Foreign Trade": {
                "japan-1905": [
                    "Foreign Trade"
                ],
                "japan-1910": [
                    "Foreign Trade"
                ],
                "japan-1920-21": [
                    "Foreign Trade"
                ],
                "japan-1930": [
                    "Foreign Trade"
                ],
                "japan-1935": [
                    "Foreign Trade"
                ],
                "japan-1939-40": [
                    "Foreign Trade"
                ],
                "japan-1946-48": [
                    "Foreign Trade"
                ]
            },
            "Communications (Post, Telegraph, Telephone)": {
                "japan-1905": [
                    "Communications",
                    "Communications (Post, Telegraph and Telephone)"
                ],
                "japan-1910": [
                    "Communications"
                ],
                "japan-1920-21": [
                    "Communications"
                ],
                "japan-1930": [
                    "Post, Telegraph & Telephone"
                ],
                "japan-1935": [
                    "Communications"
                ],
                "japan-1939-40": [
                    "Communications"
                ],
                "japan-1946-48": [
                    "Communications"
                ]
            },
            "Railways and Land Transport": {
                "japan-1905": [
                    "Railways"
                ],
                "japan-1910": [
                    "Railways"
                ],
                "japan-1920-21": [
                    "Railways"
                ],
                "japan-1930": [
                    "Railways"
                ],
                "japan-1935": [
                    "Land and Air Transportation"
                ],
                "japan-1939-40": [
                    "Land and Air Transportation"
                ],
                "japan-1946-48": [
                    "Transportation"
                ]
            },
            "Shipping and Shipbuilding": {
                "japan-1905": [
                    "Mercantile Marine"
                ],
                "japan-1910": [
                    "Mercantile Marine"
                ],
                "japan-1920-21": [
                    "Mercantile Marine & Shipbuilding Industry"
                ],
                "japan-1930": [
                    "Shipping and Shipbuilding"
                ],
                "japan-1935": [
                    "Sea Transportation"
                ],
                "japan-1939-40": [
                    "Sea Transportation"
                ],
                "japan-1946-48": [
                    "Transportation"
                ]
            },
            "Public Works and Construction": {
                "japan-1910": [
                    "Construction & Public Works"
                ],
                "japan-1920-21": [
                    "Public Works"
                ],
                "japan-1930": [
                    "Construction"
                ]
            },
            "Education": {
                "japan-1905": [
                    "Education"
                ],
                "japan-1910": [
                    "Education"
                ],
                "japan-1920-21": [
                    "Education"
                ],
                "japan-1930": [
                    "Education"
                ],
                "japan-1935": [
                    "Education"
                ],
                "japan-1939-40": [
                    "Education"
                ],
                "japan-1946-48": [
                    "Education"
                ]
            },
            "Religion": {
                "japan-1905": [
                    "Religions"
                ],
                "japan-1910": [
                    "Religions and Religious Works"
                ],
                "japan-1920-21": [
                    "Religions and Religious Work"
                ],
                "japan-1930": [
                    "Religion and Religious Works"
                ],
                "japan-1935": [
                    "Religion"
                ],
                "japan-1939-40": [
                    "Religion"
                ],
                "japan-1946-48": [
                    "Religion"
                ]
            },
            "Justice, Police and Prisons": {
                "japan-1905": [
                    "Justice, Police and Sanitation"
                ],
                "japan-1910": [
                    "Justice, Prisons, Police and Sanitation"
                ],
                "japan-1920-21": [
                    "Justice, Prisons, Police and Sanitation"
                ],
                "japan-1930": [
                    "Justice, Police and Prisons"
                ],
                "japan-1935": [
                    "Justice and Police"
                ],
                "japan-1939-40": [
                    "Justice and Police"
                ],
                "japan-1946-48": [
                    "Justice and Police"
                ]
            },
            "Medicine and Sanitation": {
                "japan-1905": [
                    "Justice, Police and Sanitation"
                ],
                "japan-1910": [
                    "Justice, Prisons, Police and Sanitation"
                ],
                "japan-1920-21": [
                    "Justice, Prisons, Police and Sanitation"
                ],
                "japan-1930": [
                    "Medicine and Sanitation"
                ],
                "japan-1935": [
                    "Medicine and Sanitation"
                ],
                "japan-1939-40": [
                    "Medicine and Sanitation"
                ],
                "japan-1946-48": [
                    "Medicine and Sanitation"
                ]
            },
            "Charity, Relief and Social Work": {
                "japan-1910": [
                    "Charity and Relief"
                ],
                "japan-1920-21": [
                    "Charity and Relief"
                ],
                "japan-1930": [
                    "Social Problems and Facts"
                ],
                "japan-1935": [
                    "Social Problems and Social Works"
                ],
                "japan-1939-40": [
                    "Social Problems and Social Works"
                ],
                "japan-1946-48": [
                    "Social Work"
                ]
            },
            "Labour": {
                "japan-1910": [
                    "Social Politics & Labour Problems"
                ],
                "japan-1920-21": [
                    "Social Politics and Labor Problems"
                ],
                "japan-1930": [
                    "Labor"
                ],
                "japan-1935": [
                    "Labour and Labour Movements"
                ],
                "japan-1939-40": [
                    "Labour and Labour Movements"
                ],
                "japan-1946-48": [
                    "Labor and Labor Movement"
                ]
            },
            "Press and Publications": {
                "japan-1905": [
                    "The Press"
                ],
                "japan-1910": [
                    "The Press"
                ],
                "japan-1920-21": [
                    "Press and Publication"
                ],
                "japan-1930": [
                    "Press and Publication"
                ],
                "japan-1935": [
                    "Press and Publications"
                ],
                "japan-1939-40": [
                    "Press and Publications"
                ],
                "japan-1946-48": [
                    "Press and Publications"
                ]
            },
            "Arts, Literature and Music": {
                "japan-1910": [
                    "Arts and Crafts of Modern Japan"
                ],
                "japan-1920-21": [
                    "Arts and Crafts"
                ],
                "japan-1930": [
                    "Arts and Crafts"
                ],
                "japan-1935": [
                    "Literature, Arts and Music"
                ],
                "japan-1939-40": [
                    "Literature, Arts and Music"
                ],
                "japan-1946-48": [
                    "Literature, Arts and Music"
                ]
            },
            "Sports": {
                "japan-1920-21": [
                    "Sports and Amusements",
                    "Sports and Amusement"
                ],
                "japan-1930": [
                    "Sports"
                ],
                "japan-1935": [
                    "Sports"
                ],
                "japan-1939-40": [
                    "Sports"
                ],
                "japan-1946-48": [
                    "Sports"
                ]
            },
            "Amusements": {
                "japan-1920-21": [
                    "Sports and Amusements",
                    "Sports and Amusement"
                ],
                "japan-1930": [
                    "Amusements"
                ],
                "japan-1935": [
                    "Amusements and Calendar of Annual Events"
                ],
                "japan-1939-40": [
                    "Amusements and Calendar of Annual Events"
                ],
                "japan-1946-48": [
                    "Amusements and Calendar of Annual Events"
                ]
            },
            "Great Cities": {
                "japan-1930": [
                    "Six Premier Cities"
                ],
                "japan-1935": [
                    "Tokyo",
                    "Five Big Cities"
                ],
                "japan-1939-40": [
                    "Tokyo",
                    "Five Big Cities"
                ]
            },
            "Korea (Chosen)": {
                "japan-1905": [
                    "Korea"
                ],
                "japan-1910": [
                    "Korea"
                ],
                "japan-1920-21": [
                    "Chosen (Korea)"
                ],
                "japan-1930": [
                    "Chosen (Korea)"
                ],
                "japan-1935": [
                    "Chosen (Korea)"
                ],
                "japan-1939-40": [
                    "Chosen (Korea)",
                    "Chosen"
                ]
            },
            "Taiwan (Formosa)": {
                "japan-1905": [
                    "Formosa"
                ],
                "japan-1910": [
                    "Formosa"
                ],
                "japan-1920-21": [
                    "Taiwan (Formosa)"
                ],
                "japan-1930": [
                    "Taiwan (Formosa)"
                ],
                "japan-1935": [
                    "Taiwan (Formosa)"
                ],
                "japan-1939-40": [
                    "Taiwan (Formosa)"
                ]
            },
            "Karafuto (Saghalien)": {
                "japan-1910": [
                    "Karafuto"
                ],
                "japan-1920-21": [
                    "Karafuto (Saghalien)"
                ],
                "japan-1930": [
                    "Karafuto (Saghalien, Southern Half Below 50°)"
                ],
                "japan-1935": [
                    "Karafuto (Saghalien)"
                ],
                "japan-1939-40": [
                    "Karafuto (Saghalien)",
                    "Karafuto"
                ]
            },
            "South Manchuria and Manchoukuo": {
                "japan-1910": [
                    "South Manchuria"
                ],
                "japan-1920-21": [
                    "South Manchuria, the South Sea Islands and Tsingtao"
                ],
                "japan-1930": [
                    "South Manchuria & South Sea Islands",
                    "South Manchuria and the South Sea Islands"
                ],
                "japan-1935": [
                    "Manchoukuo"
                ],
                "japan-1939-40": [
                    "Manchoukuo"
                ]
            },
            "South Sea Islands": {
                "japan-1920-21": [
                    "South Manchuria, the South Sea Islands and Tsingtao"
                ],
                "japan-1930": [
                    "South Manchuria & South Sea Islands",
                    "South Manchuria and the South Sea Islands"
                ],
                "japan-1935": [
                    "South Sea Islands under Japan's Mandate"
                ],
                "japan-1939-40": [
                    "South Sea Islands under Japan's Mandate"
                ]
            },
            "Progress of Science": {
                "japan-1935": [
                    "Progress of Science"
                ],
                "japan-1939-40": [
                    "Progress of Science"
                ]
            },
            "Customs Tariff": {
                "japan-1905": [
                    "Appendix: Import Tariff List"
                ],
                "japan-1935": [
                    "Appendix: Customs Tariff"
                ]
            }
        }
    },
    "china": {
        "name": "The China Year Book",
        "books": [
            "china-1912",
            "china-1922",
            "china-1929-30",
            "china-1938"
        ],
        "topics": {
            "Calendar": {
                "china-1912": [
                    "Calendars"
                ],
                "china-1938": [
                    "Calendar"
                ]
            },
            "General Information: Area and Population": {
                "china-1912": [
                    "The Chinese Empire"
                ],
                "china-1922": [
                    "Area and Population of China",
                    "Geography"
                ],
                "china-1929-30": [
                    "General Information"
                ],
                "china-1938": [
                    "General Information"
                ]
            },
            "Fauna": {
                "china-1912": [
                    "Fauna"
                ],
                "china-1922": [
                    "Fauna"
                ]
            },
            "Climate and Meteorology": {
                "china-1912": [
                    "Climate and Meteorology"
                ],
                "china-1922": [
                    "Climate & Meteorology"
                ],
                "china-1938": [
                    "The Climate of China"
                ]
            },
            "People and Language": {
                "china-1912": [
                    "People and Language"
                ],
                "china-1922": [
                    "People & Language"
                ]
            },
            "Products and Agriculture": {
                "china-1912": [
                    "Products"
                ],
                "china-1922": [
                    "Products"
                ],
                "china-1929-30": [
                    "Products—General, Pastoral and Agricultural"
                ]
            },
            "Mines and Minerals": {
                "china-1912": [
                    "Mines and Mining"
                ],
                "china-1922": [
                    "Mines and Minerals"
                ],
                "china-1929-30": [
                    "Mines and Minerals"
                ],
                "china-1938": [
                    "Mineral Industry"
                ]
            },
            "Money, Currency and Banking": {
                "china-1912": [
                    "Money, Weights and Measures"
                ],
                "china-1922": [
                    "Money, Weights & Measures",
                    "Currency"
                ],
                "china-1929-30": [
                    "Currency, Banks, Weights and Measures"
                ],
                "china-1938": [
                    "Currency and Banking"
                ]
            },
            "Manufactures and Industry": {
                "china-1912": [
                    "Manufactures"
                ],
                "china-1922": [
                    "Manufactures"
                ],
                "china-1938": [
                    "Modern Chinese Industries"
                ]
            },
            "Commerce": {
                "china-1912": [
                    "Commerce"
                ],
                "china-1922": [
                    "Commerce"
                ],
                "china-1929-30": [
                    "Trade and Commerce"
                ],
                "china-1938": [
                    "The Foreign Trade of China"
                ]
            },
            "Customs Revenue and Trade Statistics": {
                "china-1912": [
                    "Trade Statistics",
                    "Trade Statistics—Silk",
                    "Trade Statistics—Tea",
                    "Trade Statistics—Bullion",
                    "Trade Statistics—Bullion and Specie"
                ],
                "china-1922": [
                    "Customs Revenue and Trade Statistics"
                ],
                "china-1929-30": [
                    "Customs Revenue and Trade Returns"
                ],
                "china-1938": [
                    "Customs Revenue and Trade Statistics"
                ]
            },
            "Customs Tariff": {
                "china-1922": [
                    "The Chinese Customs Tariff"
                ],
                "china-1929-30": [
                    "Customs Import Tariff of the Republic of China"
                ],
                "china-1938": [
                    "Customs Import Tariff of the Republic of China"
                ]
            },
            "Communications": {
                "china-1912": [
                    "Communications",
                    "The Chinese Imperial Post Office"
                ],
                "china-1922": [
                    "Communications"
                ],
                "china-1929-30": [
                    "Communications—Railways and Roads",
                    "Communications—Posts, Telegraphs and Aviation"
                ],
                "china-1938": [
                    "Communications"
                ]
            },
            "Government": {
                "china-1912": [
                    "The Government",
                    "Constitutional Reform"
                ],
                "china-1922": [
                    "The Chinese Government"
                ],
                "china-1929-30": [
                    "The Chinese Government",
                    "The Kuomintang"
                ],
                "china-1938": [
                    "The Kuomintang and the Government"
                ]
            },
            "Army and Navy": {
                "china-1912": [
                    "Defence",
                    "The Navy"
                ],
                "china-1922": [
                    "Defence"
                ],
                "china-1929-30": [
                    "Army and Navy"
                ],
                "china-1938": [
                    "Army and Navy"
                ]
            },
            "Finance": {
                "china-1912": [
                    "Finance"
                ],
                "china-1922": [
                    "Finance",
                    "The New Consortium"
                ],
                "china-1929-30": [
                    "Finance"
                ],
                "china-1938": [
                    "Finance"
                ]
            },
            "Shipping": {
                "china-1912": [
                    "Shipping"
                ],
                "china-1929-30": [
                    "Shipping"
                ],
                "china-1938": [
                    "Shipping"
                ]
            },
            "Education": {
                "china-1912": [
                    "Education"
                ],
                "china-1922": [
                    "Education"
                ],
                "china-1929-30": [
                    "Education"
                ],
                "china-1938": [
                    "Education"
                ]
            },
            "Religions": {
                "china-1912": [
                    "Religions"
                ],
                "china-1922": [
                    "Religions"
                ],
                "china-1929-30": [
                    "Religions"
                ],
                "china-1938": [
                    "Religions"
                ]
            },
            "Public Justice": {
                "china-1922": [
                    "Public Justice"
                ],
                "china-1929-30": [
                    "Public Justice"
                ],
                "china-1938": [
                    "Public Justice"
                ]
            },
            "River Conservancy and Harbours": {
                "china-1922": [
                    "River Conservancy & Harbour Works"
                ],
                "china-1929-30": [
                    "River Conservancy and Harbour Works"
                ],
                "china-1938": [
                    "River Conservancy and Harbours"
                ]
            },
            "Public Health": {
                "china-1929-30": [
                    "Public Health and Medical Events during 1927 and 1928"
                ],
                "china-1938": [
                    "Public Health"
                ]
            },
            "Labour": {
                "china-1929-30": [
                    "Labour"
                ],
                "china-1938": [
                    "Labour"
                ]
            },
            "Colonies, Leased Territories and Concessions": {
                "china-1929-30": [
                    "Colonies, Leased Territories and Settlements"
                ],
                "china-1938": [
                    "Colonies, Leased Territories, Concessions, Etc.",
                    "Colonies, Leased Territories, Concessions, etc."
                ]
            },
            "Greater China": {
                "china-1929-30": [
                    "Greater China"
                ],
                "china-1938": [
                    "Greater China"
                ]
            },
            "International Problems": {
                "china-1922": [
                    "China's War & Post-War Problems"
                ],
                "china-1929-30": [
                    "China's International Problems"
                ]
            },
            "Miscellaneous": {
                "china-1912": [
                    "Miscellaneous"
                ],
                "china-1922": [
                    "Miscellaneous"
                ],
                "china-1929-30": [
                    "Miscellaneous"
                ],
                "china-1938": [
                    "Miscellaneous"
                ]
            }
        }
    },
    "china-handbook": {
        "name": "China Handbook",
        "books": [
            "china-1937-43",
            "china-1950"
        ],
        "topics": {
            "General Information": {
                "china-1937-43": [
                    "Chapter I. General Information",
                    "General Information"
                ],
                "china-1950": [
                    "General Information"
                ]
            },
            "Government Structure": {
                "china-1937-43": [
                    "Government Structure"
                ],
                "china-1950": [
                    "Government Structure"
                ]
            },
            "Political Parties": {
                "china-1937-43": [
                    "The Kuomintang"
                ],
                "china-1950": [
                    "Political Parties"
                ]
            },
            "Public Finance": {
                "china-1937-43": [
                    "Public Finance"
                ],
                "china-1950": [
                    "Public Finance"
                ]
            },
            "Communications": {
                "china-1937-43": [
                    "Communications"
                ],
                "china-1950": [
                    "Communications",
                    "Postal Service and Tele-Communications"
                ]
            },
            "Courts, Police and Prisons": {
                "china-1937-43": [
                    "Courts and Prisons"
                ],
                "china-1950": [
                    "Judicial System and Police"
                ]
            },
            "Military Affairs and Defence": {
                "china-1937-43": [
                    "Military Affairs"
                ],
                "china-1950": [
                    "National Defense"
                ]
            },
            "Education": {
                "china-1937-43": [
                    "Education and Research"
                ],
                "china-1950": [
                    "Education"
                ]
            },
            "Industry": {
                "china-1937-43": [
                    "Industry and Labor"
                ],
                "china-1950": [
                    "Industry"
                ]
            },
            "Labour": {
                "china-1937-43": [
                    "Industry and Labor"
                ],
                "china-1950": [
                    "Labor"
                ]
            },
            "Mineral Resources": {
                "china-1937-43": [
                    "Mineral Resources"
                ],
                "china-1950": [
                    "Mineral Resources"
                ]
            },
            "Money and Banking": {
                "china-1937-43": [
                    "Money and Banking"
                ],
                "china-1950": [
                    "Banking"
                ]
            },
            "Foreign Trade": {
                "china-1937-43": [
                    "Foreign Trade"
                ],
                "china-1950": [
                    "Foreign Trade"
                ]
            },
            "Agriculture": {
                "china-1937-43": [
                    "Agricultural Economy"
                ],
                "china-1950": [
                    "Agriculture",
                    "Food",
                    "Forestry, Animal Husbandry and Fisheries",
                    "Land"
                ]
            },
            "Prices": {
                "china-1937-43": [
                    "Price and Commodity Control"
                ],
                "china-1950": [
                    "Commodity Prices"
                ]
            },
            "Public Health and Medicine": {
                "china-1937-43": [
                    "Public Health and Medicine"
                ],
                "china-1950": [
                    "Public Health and Medicine"
                ]
            },
            "The Press": {
                "china-1937-43": [
                    "The Press"
                ],
                "china-1950": [
                    "The Press"
                ]
            },
            "Relief": {
                "china-1937-43": [
                    "Relief Activities"
                ],
                "china-1950": [
                    "Relief and Rehabilitation"
                ]
            }
        }
    },
    "korea-jijo": {
        "name": "朝鮮事情 (Chōsen jijō)",
        "books": [
            "korea-1935",
            "korea-1940",
            "korea-1942",
            "korea-1943",
            "korea-1944"
        ],
        "topics": {
            "總說 General Survey": {
                "korea-1935": [
                    "第一章 總說"
                ],
                "korea-1940": [
                    "一 總說"
                ],
                "korea-1942": [
                    "一 總說"
                ],
                "korea-1943": [
                    "一 總說"
                ],
                "korea-1944": [
                    "一 總說"
                ]
            },
            "行政 Administration": {
                "korea-1940": [
                    "二 行政組織"
                ],
                "korea-1942": [
                    "二 行政"
                ],
                "korea-1943": [
                    "二 行政"
                ]
            },
            "財政 Finance": {
                "korea-1935": [
                    "第六章 財政及經濟"
                ],
                "korea-1940": [
                    "三 財政"
                ],
                "korea-1942": [
                    "三 財政"
                ],
                "korea-1943": [
                    "九 財政"
                ],
                "korea-1944": [
                    "九 財政"
                ]
            },
            "金融 Banking": {
                "korea-1935": [
                    "第六章 財政及經濟"
                ],
                "korea-1940": [
                    "一四 金融"
                ],
                "korea-1942": [
                    "四 金融"
                ],
                "korea-1943": [
                    "一〇 金融"
                ],
                "korea-1944": [
                    "一〇 金融"
                ]
            },
            "教育 Education": {
                "korea-1935": [
                    "第五章 教育"
                ],
                "korea-1940": [
                    "四 教育"
                ],
                "korea-1942": [
                    "一五 教育"
                ],
                "korea-1943": [
                    "一五 教育"
                ],
                "korea-1944": [
                    "一五 教育"
                ]
            },
            "地籍圖・林野圖及地形圖 Maps": {
                "korea-1935": [
                    "第十九章 地籍圖・林野圖及地形圖"
                ],
                "korea-1940": [
                    "五 地籍圖・林野圖及地形圖"
                ]
            },
            "警察 Police": {
                "korea-1935": [
                    "第十六章 警察"
                ],
                "korea-1940": [
                    "一〇 警察"
                ]
            },
            "衞生 Public Health": {
                "korea-1935": [
                    "第十七章 衞生"
                ],
                "korea-1940": [
                    "一一 衛生"
                ],
                "korea-1942": [
                    "二〇 衞生"
                ],
                "korea-1943": [
                    "二〇 衞生"
                ],
                "korea-1944": [
                    "二〇 衞生"
                ]
            },
            "專賣 Monopolies": {
                "korea-1935": [
                    "第七章 專賣"
                ],
                "korea-1940": [
                    "一二 專賣"
                ],
                "korea-1942": [
                    "一二 專賣"
                ],
                "korea-1943": [
                    "一二 專賣"
                ],
                "korea-1944": [
                    "一二 專賣"
                ]
            },
            "交通・通信 Transport and Communications": {
                "korea-1935": [
                    "第二章 交通"
                ],
                "korea-1940": [
                    "一三 交通通信"
                ],
                "korea-1942": [
                    "一三 交通・通信"
                ],
                "korea-1943": [
                    "一三 交通・通信"
                ],
                "korea-1944": [
                    "一三 交通・通信"
                ]
            },
            "農業 Agriculture": {
                "korea-1935": [
                    "第八章 農業"
                ],
                "korea-1940": [
                    "一五 農業",
                    "一七 農山漁村の振興・更生事業"
                ],
                "korea-1942": [
                    "五 農業"
                ],
                "korea-1943": [
                    "三 農業"
                ],
                "korea-1944": [
                    "三 農業"
                ]
            },
            "林業 Forestry": {
                "korea-1935": [
                    "第十二章 林業"
                ],
                "korea-1940": [
                    "一六 林業"
                ],
                "korea-1942": [
                    "六 林業"
                ],
                "korea-1943": [
                    "四 林業"
                ],
                "korea-1944": [
                    "四 林業"
                ]
            },
            "水產業 Fisheries": {
                "korea-1935": [
                    "第十四章 水產業"
                ],
                "korea-1940": [
                    "一八 水産業"
                ],
                "korea-1942": [
                    "七 水產業"
                ],
                "korea-1943": [
                    "五 水產業"
                ],
                "korea-1944": [
                    "五 水產業"
                ]
            },
            "鑛業 Mining": {
                "korea-1935": [
                    "第十三章 鑛業"
                ],
                "korea-1940": [
                    "一九 鑛業"
                ],
                "korea-1942": [
                    "八 鑛業"
                ],
                "korea-1943": [
                    "六 鑛業"
                ],
                "korea-1944": [
                    "六 鑛業"
                ]
            },
            "工業 Manufacturing Industry": {
                "korea-1935": [
                    "第十章 工業"
                ],
                "korea-1940": [
                    "二〇 工業"
                ],
                "korea-1942": [
                    "九 工業"
                ],
                "korea-1943": [
                    "七 工業"
                ],
                "korea-1944": [
                    "七 工業"
                ]
            },
            "商業 Commerce": {
                "korea-1935": [
                    "第九章 商業"
                ],
                "korea-1940": [
                    "二一 商業"
                ],
                "korea-1942": [
                    "一〇 商業"
                ],
                "korea-1943": [
                    "八 商業"
                ],
                "korea-1944": [
                    "八 商業"
                ]
            },
            "貿易 Trade": {
                "korea-1935": [
                    "第十一章 貿易"
                ],
                "korea-1940": [
                    "二三 貿易"
                ],
                "korea-1942": [
                    "一一 貿易"
                ],
                "korea-1943": [
                    "一一 貿易"
                ],
                "korea-1944": [
                    "一一 貿易"
                ]
            },
            "軍事 Military Affairs": {
                "korea-1935": [
                    "第二十二章 軍事"
                ],
                "korea-1940": [
                    "二六 軍事"
                ],
                "korea-1942": [
                    "二六 軍事"
                ],
                "korea-1943": [
                    "二六 軍事"
                ],
                "korea-1944": [
                    "二六 軍事"
                ]
            },
            "在外朝鮮人 Koreans Abroad": {
                "korea-1940": [
                    "二七 在外朝鮮人に對する保護施設"
                ],
                "korea-1942": [
                    "二七 在外朝鮮人に對する保護施設"
                ],
                "korea-1943": [
                    "二七 在外朝鮮人に對する保護施設"
                ],
                "korea-1944": [
                    "二七 在外朝鮮人に對する保護施設"
                ]
            },
            "附錄 參考統計表 Reference Statistical Tables": {
                "korea-1940": [
                    "附錄 參考統計表"
                ],
                "korea-1942": [
                    "附錄 參考統計表"
                ],
                "korea-1943": [
                    "附錄 參考統計表"
                ],
                "korea-1944": [
                    "附錄 參考統計表"
                ]
            },
            "附錄 朝鮮地圖 Map of Korea (place list)": {
                "korea-1940": [
                    "附錄 朝鮮地圖"
                ],
                "korea-1942": [
                    "附錄 朝鮮地圖"
                ],
                "korea-1943": [
                    "附錄 朝鮮地圖"
                ],
                "korea-1944": [
                    "附錄 朝鮮地圖"
                ]
            }
        }
    }
}

# Annual Report on Reforms and Progress / Administration of Chosen (English, Government-General), 1911-12 to 1929-30.
# Combined chapters (e.g. "Finance and Economy", "Production and Industry") sit under several topics.
_KA_BOOKS = ["korea-1907", "korea-1908-09", "korea-1909-10", "korea-1910-11", "korea-1911-12", "korea-1912-13", "korea-1913-14", "korea-1914-15", "korea-1915-16", "korea-1916-17",
             "korea-1917-18", "korea-1918-21", "korea-1921-22", "korea-1922-23", "korea-1923-24", "korea-1924-25",
             "korea-1926-27", "korea-1927-28", "korea-1928-29", "korea-1929-30"]
_KA = {
    "General survey and population": {
        "Front Matter": "*", "Introduction": "*", "General Remarks": "*",
        "I. Central Administration": "*", "I. General Administration": "*", "I. Government Organization": "*",
        "Government Organization": "*"},
    "Local administration": {
        "II. Local Administration": "*", "XVIII. Local Administration": "*", "Local Administration": "*"},
    "Justice and prisons": {"III. Justice": "*", "XIV. Justice": "*", "Justice": "*"},
    "Police and peace and order": {"IV. Peace and Order": "*", "XV. Peace and Order": "*", "Police": "*"},
    "Finance": {"V. Finance": "*", "II. Finance": "*", "Finance": "*", "Finance and Economy": "*"},
    "Currency and banking": {"VI. Currency, Banking, etc.": "*", "VI. Currency and Banking": "*",
                             "IV. Currency, Banking, etc.": "*", "Economic Conditions": "*", "Finance and Economy": "*"},
    "Government undertakings and monopolies": {"VII. Government Undertakings": "*", "III. Government Undertakings": "*",
                                               "Finance and Economy": "*"},
    "Civil engineering": {"VIII. Civil Engineering Works": "*", "VIII. Civil Engineering": "*",
                          "VII. Civil Engineering Works": "*", "Civil Engineering": "*", "XVII. Investigation Works": "*"},
    "Communications and transport": {"IX. Communications": "*", "VI. Traffic and Communication": "*", "Communications": "*"},
    "Commerce and foreign trade": {"X. Commerce": "*", "V. Foreign Trade": "*", "V. Trade": "*",
                                   "Economic Conditions": "*", "Finance and Economy": "*"},
    "Agriculture": {"XI. Agriculture": "*", "VIII. Agriculture": "*", "Industry": "*",
                    "Production and Industry": "*", "Industries": "*"},
    "Companies and manufacturing": {"XII. Trade and Industry": "*", "IX. Trade and Industry": "*", "Industry": "*",
                                    "Production and Industry": "*", "Industries": "*", "Economic Conditions": "*"},
    "Mining, forestry and fishery": {"XIII. Forestry": "*", "XIV. Mining": "*", "XV. Fishery": "*", "XV. Fishing": "*",
                                     "XIII. Mining, Forestry and Fishery": "*", "XIII. Mining": "*", "XIV. Forestry": "*",
                                     "X. Mining": "*", "XI. Forestry": "*", "XII. Fishery": "*", "Industry": "*",
                                     "Production and Industry": "*", "Industries": "*"},
    "Sanitation": {"XVI. Sanitation": "*", "XIV. Sanitation": "*", "Sanitation": "*", "Public Hygiene": "*"},
    "Education": {"XVII. Education": "*", "XV. Education": "*", "XIII. Education": "*", "Education": "*"},
    "Religion and charity": {"Shrines and Religion": "*", "Shrines and Religions": "*", "Charity and Relief": "*"},
    "Statistical appendix": {"Statistical Tables": "*", "Statistics": "*", "Tables": "*", "Appendix": "*"},
}
_KA_EXTRA = {  # 1907-1911 reports (user, 2026-10-28)
    "General survey and population": ["Introduction", "General", "Imperial Household", "Central Administration", "Administration"],
    "Local administration": ["Local Administration", "Japanese Settlement Municipality Administration"],
    "Justice and prisons": ["Judiciary", "Justice"],
    "Police and peace and order": ["Peace and Order", "Defence"],
    "Finance": ["Finance"],
    "Currency and banking": ["Currency", "Banking, Etc", "Currency, Banking, Etc"],
    "Government undertakings and monopolies": ["Government Undertakings", "Public Undertakings"],
    "Communications and transport": ["Communications"],
    "Commerce and foreign trade": ["Commerce", "Foreign Commerce"],
    "Agriculture": ["Agriculture", "Agricultural, and Industrial"],
    "Companies and manufacturing": ["Trade and Industry", "Agricultural, and Industrial"],
    "Mining, forestry and fishery": ["Mining", "Forestry", "Fishery", "Mining, Forestry and Fishing", "Mining, Forestry and Fishery"],
    "Sanitation": ["Sanitation"],
    "Education": ["Education", "Education, Etc"],
    "Religion and charity": ["Charities"],
}
import re as _re
def _kan(c): return _re.sub(r'[^a-z, ]', '', _re.sub(r'^[IVXL]+\.\s*', '', str(c or '')).lower()).strip(' ,')


def _ka_topics():
    import json, os
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    chs = {}
    for b in _KA_BOOKS:
        f = os.path.join(d, b + ".json")
        if os.path.exists(f):
            with open(f, encoding="utf-8") as fh:
                chs[b] = list(dict.fromkeys(t.get("chapter") for t in json.load(fh)))
    out = {}
    for topic, names in _KA.items():
        extra = {_kan(x) for x in _KA_EXTRA.get(topic, [])} | {_kan(x) for x in names}
        m = {b: [c for c in cs if c in names or (b in _KA_BOOKS[:4] and _kan(c) in extra)] for b, cs in chs.items()}
        m = {b: v for b, v in m.items() if v}
        if len(m) >= 2:
            out[topic] = m
    return out


SERIES["korea-annual"] = {"name": "Annual Report on Reforms and Progress / Administration of Chosen",
                          "books": _KA_BOOKS, "topics": _ka_topics()}


_JT = ["japan-tokei-1935", "japan-tokei-1938", "japan-tokei-1940"]
_jt = lambda a, b, c: {k: v for k, v in zip(_JT, (a, b, c)) if v}
SERIES["japan-tokei"] = {"name": "大日本帝國統計年鑑 (Statistical Yearbook of the Empire of Japan)", "books": _JT, "topics": {
    "Weights, measures and currency": _jt(["度量衡比較及合數", "貨幣純分比價及爲替相場"], ["度量衡比較及合數", "貨幣純分比價及爲替相場"], ["度量衡比較、合數及略算法"]),
    "Land and climate": _jt(["1 土地及氣象"], ["1 土地"], ["1 土地"]),
    "Population": _jt(["2 人口"], ["2 人口"], ["2 人口"]),
    "Agriculture, forestry and fisheries": _jt(["3 農林及水産"], ["3 農林及水産"], ["3 農林及水產"]),
    "Mining and industry": _jt(["4 鑛業及工業"], ["4 鑛業及工業"], ["4 工業"]),
    "Commerce and banking": _jt(["5 商業及金融"], ["5 商業及金融", "15 産業團體"], ["5 商業及金融"]),
    "Foreign trade": _jt(["6 貿易"], ["6 貿易"], ["6 貿易"]),
    "Transport and communications": _jt(["7 交通"], ["7 交通"], ["7 交通"]),
    "Social work and welfare": _jt(["8 社會事業"], ["8 社會事業"], ["8 厚生"]),
    "Labour": _jt(["9 勞働"], ["9 勞働及職業紹介"], ["9 勞働"]),
    "Education, shrines and religion": _jt(["10 教育及宗教"], ["10 教育、神社及宗教"], ["10 教育、神社及宗教"]),
    "Police, public health and disasters": _jt(["11 警察、衞生及災害"], ["11 警察、衛生及災害"], ["11 警察、衛生及災害"]),
    "Justice": _jt(["12 司法"], ["12 司法"], ["12 司法"]),
    "Public finance": _jt(["13 財政"], ["13 財政"], ["13 財政"]),
    "Elections, officials, military, honours and pensions": _jt(["14 選擧、官公吏、軍事及恩賞"], ["14 選擧、官公吏、軍事及恩賞"], ["14 恩給其ノ他"]),
    "International tables": _jt(["國際統計表"], ["國際統計表"], None)}}


_NY = ["nanyo-tokei-1932", "nanyo-tokei-1933", "nanyo-tokei-1934", "nanyo-tokei-1935", "nanyo-tokei-1936", "nanyo-tokei-1937",
       "nanyo-tokei-1938", "nanyo-tokei-1939"]
_NYCH = [("Land and climate", "I 土地及氣象", "1 土地"), ("Population", "II 戶口", "2 戸口"), ("Administration", "III 行政", "3 行政"),
         ("Police", "IV 警察", "4 警察"), ("Public health", "V 衛生", "5 衞生"), ("Justice and prisons", "VI 司法行刑", "6 司法行刑"),
         ("Education", "VII 敎育", "7 敎育"), ("Religion", "VIII 宗敎", "8 宗敎"), ("Industry", "IX 產業", "9 產業"),
         ("Transport and communications", "X 交通及通信", "10 交通及通信"), ("Finance and prices", "XI 金融", "11 金融"),
         ("Trade", "XII 貿易", "12 貿易"), ("Public finance", "XIII 財政", "13 財政"), ("Social work", "XIV 社會事業", "14 社會事業"),
         ("Appendix", "附錄", "附錄")]
def _ny_topics():  # chapters are numbered alike in every edition (I/1 … XIV/14, 附錄); match by number
    import json, os
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    ROMAN = {r: i for i, r in enumerate("I II III IV V VI VII VIII IX X XI XII XIII XIV".split(), 1)}
    num = lambda c: ROMAN.get(str(c).split()[0], None) or (int(str(c).split()[0]) if str(c).split()[0].isdigit() else str(c))
    out = {}
    for b in _NY:
        f = os.path.join(d, b + ".json")
        if not os.path.exists(f): continue
        for c in dict.fromkeys(t.get("chapter") for t in json.load(open(f, encoding="utf-8"))):
            for k, (t, a, _) in enumerate(_NYCH, 1):
                if num(c) == (k if a != "附錄" else "附錄"): out.setdefault(t, {}).setdefault(b, []).append(c)
    return out
SERIES["nanyo-tokei"] = {"name": "南洋廳統計年鑑 (Statistical Yearbook of the South Seas Government)", "books": _NY,
                         "topics": _ny_topics()}

# Japan's annual report to the League of Nations on the South Sea Islands: English editions and the Japanese edition
# (日本帝國委任統治地域行政年報) of the same report (user, 2026-10-28)
_SM = ["mandate-report-1925", "gyosei-nenpo-1928", "gyosei-nenpo-1929", "mandate-report-1930", "mandate-report-1931"]
_SMK = [("General remarks, area and climate", ["General Remarks", "總說"]),
        ("Administration, police and justice", ["Administration", "行政一般", "Justice"]),
        ("Finance", ["Financ", "財政"]),
        ("Education", ["Education", "敎育", "教育"]),
        ("Religion", ["Religion", "宗敎", "宗教"]),
        ("Industry, land and labour", ["Industry", "產業", "産業", "Land System", "土地制度", "Labour", "勞働", "Mining"]),
        ("Communications, navigation and trade", ["Communication", "通信", "Navigation", "Trade", "貿易"]),
        ("Welfare of the islanders and population", ["Well-being", "福祉", "Population", "人口"]),
        ("Public health", ["Public Health", "衞生年報", "衛生年報"]),
        ("Laws and regulations", ["Laws", "法令"])]
def _sm_topics():
    import json, os
    d = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data")
    out = {}
    for b in _SM:
        f = os.path.join(d, b + ".json")
        if not os.path.exists(f): continue
        for c in dict.fromkeys(t.get("chapter") for t in json.load(open(f, encoding="utf-8"))):
            for t, keys in _SMK:
                if c and any(k in c for k in keys):
                    out.setdefault(t, {}).setdefault(b, []).append(c); break
    return out
SERIES["south-seas-mandate"] = {"name": "Annual Report to the League of Nations on the South Sea Islands (English and Japanese editions)",
                                "books": _SM, "topics": _sm_topics()}


# Extra series / editions added from topicmaps/<series>.json (2026-10-28): {"name": ..., "books": [...], "topics":
# {topic: {slug: [chapter names]}}}. Books are merged into an existing series (kept in date order by slug); topics
# merged chapter by chapter. Topics present in only one edition are dropped.
def _merge_topicmaps():
    import json, os, glob, re
    for f in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "topicmaps", "*.json"))):
        d = json.load(open(f, encoding="utf-8")); k = os.path.basename(f)[:-5]
        S = SERIES.setdefault(k, {"name": d.get("name", k), "books": [], "topics": {}})
        S["books"] = sorted(set(S["books"]) | set(d.get("books", [])), key=lambda b: (re.search(r"(18|19)\d\d", b).group(0) if re.search(r"(18|19)\d\d", b) else "9999", b))
        for t, m in d.get("topics", {}).items():
            T = S["topics"].setdefault(t, {})
            for b, chs in m.items():
                T[b] = list(dict.fromkeys(T.get(b, []) + list(chs)))
        S["topics"] = {t: m for t, m in S["topics"].items() if len(m) >= 2}
_merge_topicmaps()

# 中華民國統計提要 (Statistical Abstract of the Republic of China): 1935 (36 classes) and 1947 (8 sections) (user, 2026-11-10)
_CT = ["china-tongji-1935", "china-tongji-1947"]
_CT_TOPICS = {
    "Area and population": {"china-tongji-1935": ["第一類 疆界與地勢", "第十類 人口"], "china-tongji-1947": ["第一類 土地與人口"]},
    "Agriculture, forestry and land": {"china-tongji-1935": ["第十九類 土地", "第二十類 農業", "第二十一類 林業", "第二十二類 漁業", "第二十三類 畜牧"],
                                        "china-tongji-1947": ["第二類 農業"]},
    "Mining, industry, commerce and prices": {"china-tongji-1935": ["第二十四類 礦業", "第二十五類 工業", "第二十六類 商業", "第二十七類 貿易", "第二十八類 物價"],
                                              "china-tongji-1947": ["第三類 礦工商業"]},
    "Public finance and banking": {"china-tongji-1935": ["第二十九類 金融", "第三十類 財政"], "china-tongji-1947": ["第四類 財政與金融"]},
    "Communications": {"china-tongji-1935": ["第三十一類 郵政", "第三十二類 電政", "第三十三類 公路", "第三十四類 鐵路", "第三十五類 航政", "第三十六類 水利及公用事業"],
                       "china-tongji-1947": ["第五類 交通"]},
    "Education": {"china-tongji-1935": ["第十三類 教育"], "china-tongji-1947": ["第六類 教育"]},
    "Social affairs and public health": {"china-tongji-1935": ["第十一類 勞工", "第十二類 合作事業", "第十四類 社會病態", "第十五類 衛生", "第十六類 保衛", "第十七類 救濟", "第十八類 人民團體"],
                                         "china-tongji-1947": ["第七類 社會與衛生"]},
    "Government, justice and officials": {"china-tongji-1935": ["第四類 政治組織與行政", "第五類 法制", "第六類 司法", "第七類 官吏與考試", "第八類 監察", "第九類 外交"],
                                          "china-tongji-1947": ["第八類 政治組織"]},
}
SERIES["china-tongji"] = {"name": "中華民國統計提要 (Statistical Abstract of the Republic of China)", "books": _CT, "topics": _CT_TOPICS}


# 朝鮮防疫統計 (Korea epidemic-prevention statistics): editions with the same 76 numbered tables in three parts
SERIES["korea-boeki"] = {"name": "朝鮮防疫統計 (Epidemic Prevention Statistics of Korea)",
                         "books": ["korea-boeki-1938", "korea-boeki-1939"],
                         "topics": {"Acute infectious diseases": {"korea-boeki-1938": ["傳染病"], "korea-boeki-1939": ["傳染病"]},
                                    "Chronic infectious diseases": {"korea-boeki-1938": ["慢性傳染病"], "korea-boeki-1939": ["慢性傳染病"]},
                                    "Endemic diseases": {"korea-boeki-1938": ["地方病"], "korea-boeki-1939": ["地方病"]}}}
SERIES["japan-kenchiku"] = {"name": "建築年鑑 (Architectural Yearbook, Architectural Institute of Japan)",
                            "books": ["japan-kenchiku-1938", "japan-kenchiku-1940", "japan-kenchiku-1942"],
                            "topics": {"Review of the year": {"japan-kenchiku-1938": ["II 建築界展望"], "japan-kenchiku-1940": ["II 建築界展望"], "japan-kenchiku-1942": ["II 建築界展望"]},
                                       "Building statistics": {"japan-kenchiku-1938": ["III 建築統計"], "japan-kenchiku-1940": ["III 建築統計"], "japan-kenchiku-1942": ["III 建築統計"]},
                                       "Completed buildings": {"japan-kenchiku-1938": ["IV 竣功建築物"], "japan-kenchiku-1940": ["IV 竣功建築物"], "japan-kenchiku-1942": ["VIII 雜誌主要寫眞索引"]},
                                       "Building laws": {"japan-kenchiku-1938": ["V 建築法規"], "japan-kenchiku-1940": ["V 建築法規"], "japan-kenchiku-1942": ["IV 建築關係法規"]},
                                       "Books, research and patents": {"japan-kenchiku-1938": ["VI 建築關係新刊圖書", "VIII 研究援助及表彰", "IX 特許、意匠登錄(建築關係)"],
                                                                       "japan-kenchiku-1940": ["VII 建築關係新刊圖書", "IX 研究援助"],
                                                                       "japan-kenchiku-1942": ["VI 建築關係新刊圖書", "IX 研究援助"]},
                                       "Offices, societies, schools and journals": {"japan-kenchiku-1938": ["X 諸官公署に於ける主なる建築關係局課", "XI 建築關係團體", "XII 建築關係學校", "XIII 建築關係雜誌及新聞"],
                                                                                    "japan-kenchiku-1940": ["XI 諸官公署に於ける主なる建築關係局課", "XII 建築關係團體", "XIII 建築關係學校", "XIV 建築關係雜誌及新聞"],
                                                                                    "japan-kenchiku-1942": ["VII 建築關係雜誌及新聞發行所", "XI 帝國學士院及帝國藝術院會員", "XII 諸官公署及營團に於ける建築關係職員", "XIII 建築關係團體竝統制組合", "XIV 建築關係教育及研究機關", "XV 諸會社に於ける營繕職員"]}}}

SERIES["china-smc"] = {"name": "Shanghai Municipal Council, Report and Budget", "books": ["china-smc-1905", "china-smc-1908", "china-smc-1909", "china-smc-1911", "china-smc-1912", "china-smc-1913", "china-smc-1914", "china-smc-1915", "china-smc-1916", "china-smc-1917", "china-smc-1918", "china-smc-1919", "china-smc-1920", "china-smc-1921", "china-smc-1922", "china-smc-1925", "china-smc-1928", "china-smc-1932", "china-smc-1934", "china-smc-1936"], "topics": {"Council, ratepayers and survey of the year": {"china-smc-1934": ["Public Utilities", "Regulation of Industrial Conditions", "Ricsha Board", "Survey of 1934"], "china-smc-1936": ["Public Utilities", "Regulation of Industrial Conditions", "Ricsha Board", "Survey of 1936"], "china-smc-1932": ["Public Utilities", "Survey for 1932"], "china-smc-1928": ["Introduction", "Council Matters", "Semaphore Service and Chinese Study", "Pension List and Municipal Staff"], "china-smc-1925": ["Introduction", "Council Matters", "Semaphore Service", "Census", "Pension List and Municipal Staff"], "china-smc-1922": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1921": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1919": ["Council Matters", "Municipal Staff"], "china-smc-1920": ["Introduction", "Council Matters", "Census", "Municipal Staff"], "china-smc-1918": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1917": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1916": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1915": ["Introduction", "Council Matters", "Municipal Staff", "Census"], "china-smc-1914": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1913": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1912": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1911": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1909": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1908": ["Introduction", "Council Matters", "Municipal Staff"], "china-smc-1905": ["Introduction", "Council Matters", "Municipal Staff", "Census"]}, "Volunteer Corps and Fire Brigade": {"china-smc-1934": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1936": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1932": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1928": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1925": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1922": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1921": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1919": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1920": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1918": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1917": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1916": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1915": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1914": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1913": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1912": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1911": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1909": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1908": ["Watch — Fire Brigade", "Watch — Volunteer Corps"], "china-smc-1905": ["Watch — Fire Brigade", "Watch — Volunteer Corps"]}, "Police, gaols and courts": {"china-smc-1934": ["Watch — Gaols", "Watch — Municipal Advocate's Report", "Watch — Police Force"], "china-smc-1936": ["Watch — Gaol Branch", "Watch — Municipal Advocate's Report", "Watch — Police Force"], "china-smc-1932": ["Watch — Gaol Branch", "Watch — Municipal Advocate's Report", "Watch — Police Force"], "china-smc-1928": ["Watch — Police Force"], "china-smc-1925": ["Watch — Police Force"], "china-smc-1922": ["Watch — Police Force"], "china-smc-1921": ["Watch — Police Force"], "china-smc-1919": ["Watch — Police Force"], "china-smc-1920": ["Watch — Police Force"], "china-smc-1918": ["Watch — Police Force"], "china-smc-1917": ["Watch — Police Force"], "china-smc-1916": ["Watch — Police Force"], "china-smc-1915": ["Watch — Police Force"], "china-smc-1914": ["Watch — Police Force"], "china-smc-1913": ["Watch — Police Force"], "china-smc-1912": ["Watch — Police Force"], "china-smc-1911": ["Watch — Police Force"], "china-smc-1909": ["Watch — Police Force"], "china-smc-1908": ["Watch — Police Force"], "china-smc-1905": ["Watch — Police Force"]}, "Public health": {"china-smc-1934": ["Health"], "china-smc-1936": ["Health"], "china-smc-1932": ["Health"], "china-smc-1928": ["Health"], "china-smc-1925": ["Health", "Health — Hospitals, Pauper Burials and Milk Supply"], "china-smc-1922": ["Health"], "china-smc-1921": ["Health"], "china-smc-1919": ["Health"], "china-smc-1920": ["Health"], "china-smc-1918": ["Health"], "china-smc-1917": ["Health"], "china-smc-1916": ["Health"], "china-smc-1915": ["Health"], "china-smc-1914": ["Health"], "china-smc-1913": ["Health"], "china-smc-1912": ["Health"], "china-smc-1911": ["Health"], "china-smc-1909": ["Health"], "china-smc-1908": ["Health"], "china-smc-1905": ["Health"]}, "Public works": {"china-smc-1934": ["Works"], "china-smc-1936": ["Works"], "china-smc-1932": ["Works"], "china-smc-1928": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1925": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department", "Sewage Treatment and Disposal"], "china-smc-1922": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department", "Sewage Treatment and Disposal"], "china-smc-1921": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1919": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department", "Sewage Treatment and Disposal"], "china-smc-1920": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department", "Sewage Treatment and Disposal"], "china-smc-1918": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department", "Sewage Treatment and Disposal"], "china-smc-1917": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1916": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1915": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1914": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1913": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1912": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1911": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1909": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Parks and Open Spaces", "Electricity Department"], "china-smc-1908": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Electricity Department"], "china-smc-1905": ["Works", "Works — Properties, Easements, Road Extensions and Land Commission", "Electricity Department"]}, "Education, orchestra and library": {"china-smc-1934": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1936": ["Education", "Public Library"], "china-smc-1932": ["Education", "Orchestra and Band"], "china-smc-1928": ["Education"], "china-smc-1925": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1922": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1921": ["Education", "Orchestra and Band"], "china-smc-1919": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1920": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1918": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1917": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1916": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1915": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1914": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1913": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1912": ["Education", "Orchestra and Band", "Public Library"], "china-smc-1911": ["Education", "Orchestra and Band"], "china-smc-1909": ["Education", "Orchestra and Band"], "china-smc-1908": ["Education", "Orchestra and Band"], "china-smc-1905": ["Education", "Orchestra and Band"]}, "Treasurer's report and revenue": {"china-smc-1934": ["Finance — Treasurer's Report"], "china-smc-1936": ["Finance — Treasurer's Report"], "china-smc-1932": ["Finance — Treasurer's Report"], "china-smc-1928": ["Finance — Treasurer's Report", "Finance — Commissioner of Revenue's Report"], "china-smc-1925": ["Finance — Treasurer's Report", "Finance — Commissioner of Revenue's Report"], "china-smc-1922": ["Finance — Treasurer's Report", "Finance — Commissioner of Revenue's Report"], "china-smc-1921": ["Finance — Treasurer's Report", "Finance — Commissioner of Revenue's Report"], "china-smc-1919": ["Finance — Treasurer's Report", "Finance — Commissioner of Revenue's Report"], "china-smc-1920": ["Finance — Treasurer's Report", "Finance — Commissioner of Revenue's Report"], "china-smc-1918": ["Finance — Treasurer's Report", "Finance — Superintendent of Revenue's Report"], "china-smc-1917": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1916": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1915": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1914": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1913": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1912": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1911": ["Finance — Treasurer's Report", "Finance — Overseer of Taxes' Report"], "china-smc-1909": ["Finance — Overseer of Taxes' Report"], "china-smc-1908": ["Finance — Overseer of Taxes' Report"], "china-smc-1905": ["Finance — Overseer of Taxes' Report"]}, "Financial statement, general": {"china-smc-1934": ["Finance — Financial Statement, General, 1934"], "china-smc-1936": ["Finance — Financial Statement, General, 1936"], "china-smc-1932": ["Finance — Financial Statement, General, 1932"], "china-smc-1928": ["Finance — Financial Statement, General, 1928"], "china-smc-1925": ["Finance — Financial Statement, General, 1925"], "china-smc-1922": ["Finance — Financial Statement, General, 1922"], "china-smc-1921": ["Finance — Financial Statement, General, 1921"], "china-smc-1919": ["Finance — Financial Statement, General, 1919"], "china-smc-1920": ["Finance — Financial Statement, General, 1920"], "china-smc-1918": ["Finance — Financial Statement, General, 1918"], "china-smc-1917": ["Finance — Financial Statement, General, 1917"], "china-smc-1916": ["Finance — Financial Statement, General, 1916"], "china-smc-1915": ["Finance — Financial Statement, General, 1915"], "china-smc-1914": ["Finance — Financial Statement, General, 1914"], "china-smc-1913": ["Finance — Financial Statement, General, 1913"], "china-smc-1912": ["Finance — Financial Statement, General, 1912"], "china-smc-1911": ["Finance — Financial Statement, General, 1911"], "china-smc-1909": ["Finance — Financial Statement, General, 1909"], "china-smc-1908": ["Finance — Financial Statement, General, 1908"], "china-smc-1905": ["Finance — Financial Statement, General, 1905"]}, "Education accounts, balance sheet and schedules": {"china-smc-1934": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1934", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1936": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1936", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1932": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1932", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1928": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1928", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1925": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1925", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1922": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1922", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1921": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1921", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1919": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1919", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1920": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1920", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1918": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1918", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1917": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1917", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1916": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1916", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1915": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1915", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1914": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1914", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1913": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1913", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1912": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1912", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1911": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1911", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1909": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1909", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1908": ["Finance — Balance Sheet", "Finance — Financial Statement, Education, 1908", "Finance — Land, Buildings, Stock and Stores", "Finance — Working Accounts"], "china-smc-1905": ["Finance — Balance Sheet", "Finance — Comparative Statements and Schedules", "Finance — Financial Statement, Education, 1905", "Finance — Working Accounts"]}, "Budget: estimates, rates and fees": {"china-smc-1934": ["Budget 1935 — Estimates", "Budget 1935 — Rates, Taxes, Dues and Fees"], "china-smc-1936": ["Budget 1937 — Estimates", "Budget 1937 — Rates, Taxes, Dues and Fees"], "china-smc-1932": ["Budget 1933 — Estimates", "Budget 1933 — Rates, Taxes, Dues and Fees"], "china-smc-1928": ["Budget 1929 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1925": ["Budget 1926 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1922": ["Budget 1923 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1921": ["Budget 1922 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1919": ["Budget 1920 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1920": ["Budget 1921 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1918": ["Budget 1919 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1917": ["Budget 1918 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1916": ["Budget 1917 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1915": ["Budget 1916 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1914": ["Budget 1915 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1913": ["Budget 1914 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1912": ["Budget 1913 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1911": ["Budget 1912 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1909": ["Budget 1910 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1908": ["Budget 1909 — Estimates and Rates, Taxes, Dues and Fees"], "china-smc-1905": ["Budget 1906 — Estimates and Rates, Taxes, Dues and Fees"]}, "Budget: general": {"china-smc-1934": ["Budget 1935 — General", "Budget 1935 — Schedule of Pensions"], "china-smc-1936": ["Budget 1937 — General", "Budget 1937 — Schedule of Pensions"], "china-smc-1932": ["Budget 1933 — General", "Budget 1933 — Schedule of Pensions"], "china-smc-1928": ["Budget 1929 — General", "Budget 1929 — Schedule of Pensions"], "china-smc-1925": ["Budget 1926 — General"], "china-smc-1922": ["Budget 1923 — General"], "china-smc-1921": ["Budget 1922 — General"], "china-smc-1919": ["Budget 1920 — General"], "china-smc-1920": ["Budget 1921 — General"], "china-smc-1918": ["Budget 1919 — General"], "china-smc-1917": ["Budget 1918 — General"], "china-smc-1916": ["Budget 1917 — General"], "china-smc-1915": ["Budget 1916 — General"], "china-smc-1914": ["Budget 1915 — General"], "china-smc-1913": ["Budget 1914 — General"], "china-smc-1912": ["Budget 1913 — General"], "china-smc-1911": ["Budget 1912 — General"], "china-smc-1909": ["Budget 1910 — General"], "china-smc-1908": ["Budget 1909 — General"], "china-smc-1905": ["Budget 1906 — General"]}, "Budget: education": {"china-smc-1934": ["Budget 1935 — Education"], "china-smc-1936": ["Budget 1937 — Education"], "china-smc-1932": ["Budget 1933 — Education"], "china-smc-1928": ["Budget 1929 — Education"], "china-smc-1925": ["Budget 1926 — Education"], "china-smc-1922": ["Budget 1923 — Education"], "china-smc-1921": ["Budget 1922 — Education"], "china-smc-1919": ["Budget 1920 — Education"], "china-smc-1920": ["Budget 1921 — Education"], "china-smc-1918": ["Budget 1919 — Education"], "china-smc-1917": ["Budget 1918 — Education"], "china-smc-1916": ["Budget 1917 — Education"], "china-smc-1915": ["Budget 1916 — Education"], "china-smc-1914": ["Budget 1915 — Education"], "china-smc-1913": ["Budget 1914 — Education"], "china-smc-1912": ["Budget 1913 — Education"], "china-smc-1911": ["Budget 1912 — Education"], "china-smc-1909": ["Budget 1910 — Education"], "china-smc-1908": ["Budget 1909 — Education"], "china-smc-1905": ["Budget 1906 — Education"]}}}
