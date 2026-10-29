"""Writes data/unanswerable_queries.json.

These are questions that the indexed contracts do not answer. Before writing them I searched
the corpus for the key words (catering, parking, drone, subtitles and so on) and found no hits.
Three kinds of queries are used so that abstention is not too easy:
1. a real contract title from the corpus with a question that contract does not answer
2. a contract title that is not in the corpus, with a normal contract question
3. a plain question with no contract title

The split of each query comes from assign_split, the same function used for the benchmark.
This file was committed before any tuning and should not be edited afterwards.
"""
import json
import sys
from pathlib import Path

# this lets the script find the src folder even though it is run from inside data
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data import UNANSWERABLE_FILE, assign_split

# kind 1: a real contract from the corpus with a question it cannot answer
REAL = [
    "Consider the Sponsorship Agreement between Jacksonville Jaguars, LLC and The ARC Group, Inc.; What catering must be provided to the crew on shoot days?",
    "Consider the Endorsement Agreement between ABG-Shaq, LLC and Papa John's International, Inc.; What is the personal cryptocurrency holding of the company directors?",
    "Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; For how long are internal WhatsApp messages retained?",
    "Consider the Joint Venture Agreement between Tate & Lyle Fermentation Products Ltd. and Igene Biotechnology, Inc. for Astaxanthin Production; Is helicopter transport covered for site visits?",
    "Consider the Gas Franchise Agreement between the Town of Vinton and Roanoke Gas Company; What is the policy on pets at company offices?",
    "Consider the Supply Agreement between Florida Chemical Company, LLC and Flotek Chemistry, LLC for Terpene Products; Which airline must be used for business travel?",
    "Consider the Walabot HOME Reseller Agreement between Vayyar Imaging Ltd. and Inde Living Holdings, Inc.; Are drones allowed for product demonstrations?",
    "Consider the Co-Branding Agreement between PC Quote, Inc. and A.B. Watley, Inc. for Market Data Software; Who provides parking for visitors at the office?",
    "Consider the Promotion Agreement between Depomed, Inc. and King Pharmaceuticals, Inc. for Glumetza; What is the policy on employee tattoos?",
    "Consider the Support and Maintenance Agreement between On2 Technologies, Inc. and Wildform, Inc.; Which languages must subtitles be provided in?",
    "Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; Is a gym membership offered to staff?",
    "Consider the Marketing and Transportation Services Agreement between Purolator Courier Ltd. and Parcelway Courier Systems Canada Ltd. (Dynamex Inc.); Are limousine services provided to executives?",
    "Consider the Sponsorship Agreement between Excite, Inc. and Vitamin Shoppe Industries Inc. for Promotion on WebCrawler Channels; Who owns the podcast rights?",
    "Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; What is the carbon offset target for each project?",
    "Consider the Intellectual Property Agreement for COVID-19 Treatment Development between Marv Enterprises, LLC, Premier Biomedical, Inc., and Technology Health, Inc.; Does the agreement cover metaverse or NFT versions of the products?",
    "Consider the Endorsement Agreement between Holiday RV Superstores, Inc. and Affinity Group, Inc. for Good Sam Branding; Is the use of emoji in advertising restricted?",
    "Consider the Agency Agreement between General Electric Capital Corporation and Duckwall-Alco Stores, Inc. for Equipment Leasing; What tuition support is given to employees?",
    "Consider the Business Affiliate Agreement between Dr. George D. Green and UNION DENTAL CORP.; Can the affiliate promote the services on TikTok?",
    "Consider the Gas Transportation Agreement between PennTex North Louisiana Operating, LLC and MRD Operating LLC; Is there a smoking policy at the compressor stations?",
    "Consider the Co-Branding and Services Agreement between RSL COM PrimeCall, Inc. and deltathree.com, Inc.; Is machine learning used to route the calls?",
    "Consider the Joint Venture Agreement between MJ Syndicated, Inc. and Simply Herbals for Manufacturing and Selling Health-Related Products; What vegan certification is required for the products?",
    "Consider the Non-Competition Agreement and Right of First Offer between Glamis Gold Ltd. and Western Copper Corporation; Are relocation expenses reimbursed for staff?",
]

# kind 2: a made up contract that is not in the corpus, with a normal contract question
NOT_IN_CORPUS = [
    "Consider the Content Distribution Agreement between Star Sports Network and Meridian Digital Platforms; Does this agreement allow sublicensing to third-party streaming platforms?",
    "Consider the Broadcast Rights Agreement between Horizon Television Ltd. and Eastern Cricket Board; When does the exclusivity period end?",
    "Consider the Master Production Services Agreement between Lakeview Studios, Inc. and Northwind Entertainment, LLC; Who owns the intellectual property in derivative works?",
    "Consider the Co-Production Agreement between Silverline Pictures and Bluebird Media Group; What is the governing law for this contract?",
    "Consider the Music Licensing Agreement between Harmony Records Corp. and Pinnacle Broadcasting Inc.; Is there a cap on liability under this contract?",
    "Consider the Content Syndication Agreement between Orbit Streaming Services and Crescent Films Ltd.; Can this contract be terminated for convenience?",
]

# kind 3: a question that does not name any contract
NO_TITLE = [
    "Does the agreement cover broadcast rights for the next Olympic Games?",
    "Are Hindi dubbing rights included for the streaming platform?",
    "What are the blockchain based royalty payment terms?",
    "Does the contract mention a sabbatical policy for creative staff?",
    "Is a cafeteria provided for employees on the production lot?",
    "What meal allowance is paid during a pandemic lockdown?",
    "Is work from home permitted for the post production team?",
    "Does the contract allow artificial intelligence to generate promotional clips?",
]


def main():
    # put all three kinds in one list and remember which kind each one is
    queries = REAL + NOT_IN_CORPUS + NO_TITLE
    kinds = ["real_title"] * len(REAL) + ["title_not_in_corpus"] * len(NOT_IN_CORPUS) + ["no_title"] * len(NO_TITLE)
    # give every query its train or test split with the same function used for the benchmark, then save
    out = [{"query": q, "kind": k, "split": assign_split(q)} for q, k in zip(queries, kinds)]
    UNANSWERABLE_FILE.write_text(json.dumps(out, indent=1), encoding="utf-8")
    train = sum(o["split"] == "train" for o in out)
    print("total:", len(out), "train:", train, "test:", len(out) - train)


if __name__ == "__main__":
    main()
