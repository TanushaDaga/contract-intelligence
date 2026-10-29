# Failure cases on train, config final

## false_abstention (8)

- query: Consider the Amendment No. 3 to Wireless Content License Agreement between Fox Mobile Entertainment, Inc. and Glu Mobile Inc.; What is the expiration date of this contract?
  - truth: GluMobileInc_20070319_S-1A_EX-10.09_436630_EX-10.09_Content License Agreement4.txt 598:989 R@3=1.00: The rights granted hereunder shall be effective as of the Effective Date and shall expire on December 31, 2006 (the "Term"); provided, however, that with respect to each Property, including Robots, Kingdom of Heaven, Mr. and Mrs. Smith, In Her Shoes, Idiocracy
  - top1: GluMobileInc_20070319_S-1A_EX-10.09_436630_EX-10.09_Content License Agreement4.txt 0:989 score=0.271: AMENDMENT NO. 3 Dated as of February 19, 2007 Reference is hereby made to that certain fully executed Wireless Content License Agreement Number 12965 dated as of December 16, 2004, as amended November 11, 2005 and March 27, 2006 (the "Agreement"), between Fox 
  - doc_score=0.43239451925475636, top1=0.271, gap=0.009
- query: Consider the Supply Agreement between Florida Chemical Company, LLC and Flotek Chemistry, LLC for Terpene Products; What is the expiration date of this contract?
  - truth: FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt 2050:2326 R@3=0.00: The "Term" shall begin on the date hereof and shall expire December 31, 2023, subject to early termination pursuant to the terms of Section 19. Flotek, may, by written notice given to FCC on or before September 30, 2023, elect for the Term to be extended to De
  - top1: FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt 14733:15729 score=0.289: 21. Remedies. If any legal action or other proceeding is brought for the enforcement of this Agreement, or because of an alleged dispute, breach, default or misrepresentation in connection with any of the provisions of this Agreement, the successful or prevail
  - doc_score=0.3536272634437956, top1=0.289, gap=0.015
- query: Consider the Supply Agreement between Florida Chemical Company, LLC and Flotek Chemistry, LLC for Terpene Products; Does this contract include any volume restrictions?
  - truth: FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt 958:1076 R@3=0.00: "Maximum Quantity" means [***] pounds of Terpene Product per Year, prorated for any partial Year included in the Term.
  - top1: FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt 18071:18963 score=0.311: 29. Multiple Counterparts. This Agreement may be executed in multiple counterparts, each of which shall be deemed an original. 30. Waiver. Any waiver by either party to be enforceable must be in writing and no waiver by either party shall constitute a continui
  - doc_score=0.3536272634437956, top1=0.311, gap=0.006
- query: Consider the Marketing and Transportation Services Agreement between Purolator Courier Ltd. and Parcelway Courier Systems Canada Ltd. (Dynamex Inc.); Is there a clause preventing the solicitation of customers in this contract?
  - truth: DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt 7291:7515 R@3=0.00: Except for the joint marketing efforts referred to in Section 3.1 (v) above, Purolator agrees not to directly or indirectly solicit next day or multiple day freight from existing sameday customers of Dynamex.
  - top1: DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt 38291:39073 score=0.307: 23.1 Neither Party shall sell, assign, subcontract, transfer or dispose of this Agreement or any part thereof, without the prior written consent of the other Party or otherwise enter into an agreement with any other Party for Services contemplated herein. 23.2
  - doc_score=0.4587831459167665, top1=0.307, gap=0.008
- query: Consider the Gas Franchise Agreement between the Town of Vinton and Roanoke Gas Company; What is the expiration date of this contract?
  - truth: RgcResourcesInc_20151216_8-K_EX-10.3_9372751_EX-10.3_Franchise Agreement.txt 1173:1257 R@3=1.00: The term of the Franchise shall be twenty (20) years, commencing on January 1, 2016.
  - top1: RgcResourcesInc_20151216_8-K_EX-10.3_9372751_EX-10.3_Franchise Agreement.txt 2301:3111 score=0.209: total dollar value of Grantee's gas sales within Locality's percentage share = the Territorial Limits of the locality total dollar value of Grantee's gas sales in the three localities For calendar year 2016, the Franchise Fee shall be paid to Grantor on or bef
  - doc_score=0.3992742403228452, top1=0.209, gap=0.000
- query: Consider the Endorsement Agreement between ABG-Shaq, LLC and Papa John's International, Inc.; Is there a minimum commitment required under this contract?
  - truth: PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt 17729:18366 R@3=0.00: At least eight (8) "Service Days", including but not limited to: 1. Production days. Up to four (4) production days (defined as a maximum of eight (8) consecutive hours each), with PAPA JOHN'S creative agency. 2. Personal appearances. CELEBRITY shall appear at
  - top1: PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt 63870:64619 score=0.312: D. Waiver. The failure at any time of any party to demand strict performance of another party of any of the terms, covenants or conditions set forth in this Agreement will not be construed as a continuing waiver or relinquishment thereof, and any party may, at
  - doc_score=0.41980704458803214, top1=0.312, gap=0.015

## span_truncation (2)

- query: Consider the Intellectual Property Agreement for COVID-19 Treatment Development between Marv Enterprises, LLC, Premier Biomedical, Inc., and Technology Health, Inc.; What licenses are granted under this contract?
  - truth: PREMIERBIOMEDICALINC_05_14_2020-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT.txt 3264:3378 R@3=0.63: THI is granted the following rights to the Applications in Appendix A and the Licensed Products derived therefrom:
  - top1: PREMIERBIOMEDICALINC_05_14_2020-EX-10.2-INTELLECTUAL PROPERTY AGREEMENT.txt 2799:3799 score=0.549: AGREEMENT 1. RECITALS. The Recitals are hereby incorporated herein by this reference, as if fully restated herein. 2. LICENSING. To the extent that terms in the 2010 Agreement/2020 Agreement are not contradicted or revised here, the terms as stated in 2010 Agr
  - doc_score=0.4431929654121793, top1=0.549, gap=0.032
- query: Consider the Joint Venture Agreement between MJ Syndicated, Inc. and Simply Herbals for Manufacturing and Selling Health-Related Products; What are the audit rights under this contract?
  - truth: MJBIOTECH,INC_12_06_2018-EX-99.01-JOINT VENTURE AGREEMENT.txt 5188:5452 R@3=0.56: Accurate and complete books of account of the transactions of the Joint Venture will be kept in accordance with generally accepted accounting principles (GAAP) and at all reasonable times will be available and open to inspection and examination by any Particip
  - top1: MJBIOTECH,INC_12_06_2018-EX-99.01-JOINT VENTURE AGREEMENT.txt 6392:7369 score=0.514: The funds of the Joint Venture will be placed in such investments and banking accounts as will be designated by the Participants. Joint Venture funds will be held in the name of the Joint Venture and will not be commingled with those of any other person or ent
  - doc_score=0.326273887968351, top1=0.514, gap=0.149

## cross_reference (27)

- query: Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; Are there any exceptions to competitive restrictions in this contract?
  - truth: BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt 33572:34034 R@3=0.00: save that nothing in this paragraph 13.2 shall prevent you from holding (with the prior written consent of the Company, which shall not be unreasonably delayed or withheld) up to three percent (3%) of the issued equity share capital of any company where those 
  - top1: BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt 41051:42013 score=0.463: 14.4 For the avoidance of doubt nothing in this paragraph 14 shall prevent you from having any dealings with any Prospective Customer or Restricted Customer in relation to any business which is not Restricted Businesses and which is not competitive with the Re
  - doc_score=0.3111064515889276, top1=0.463, gap=0.008
- query: Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; Is there a cap on liability under this contract?
  - truth: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 11380:11583 R@3=0.50: GINARES agrees that the sole and exclusive remedy for money damages related to this Agreement and the transactions contemplated hereby shall be the rights to indemnification set forth in this Section 9.
  - top1: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 17849:18849 score=0.387: 20. No Reliance No third party is entitled to rely on any of the representations, warranties and agreements contained in this Agreement. The Parties assume no liability to any third party because of any reliance on the representations, warranties and agreement
  - doc_score=0.48084359167195656, top1=0.387, gap=0.029
- query: Consider the Sponsorship Agreement between Jacksonville Jaguars, LLC and The ARC Group, Inc.; What licenses are granted under this contract?
  - truth: ArcGroupInc_20171211_8-K_EX-10.1_10976103_EX-10.1_Sponsorship Agreement.txt 1697:2488 R@3=0.87: Subject to the terms and conditions of this Agreement, as part of the consideration of the full and timely payment of the Sponsor Fees, Club hereby grants to Sponsor, and Sponsor hereby accepts, solely in the Territory, and during the Term: (i) the right to us
  - top1: ArcGroupInc_20171211_8-K_EX-10.1_10976103_EX-10.1_Sponsorship Agreement.txt 2700:3700 score=0.396: mited to the Territory, or during any period before or after the Term. The rights granted to Sponsor pursuant to this Section 2 may not be used to promote or advertise any products or services of Sponsor other than the Sponsor Business, or any other person or 
  - doc_score=0.326508937468671, top1=0.396, gap=0.037
- query: Consider the Service Agreement between Theravance Biopharma UK Limited and Brett Haumann; What is the expiration date of this contract?
  - truth: THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt 4382:4705 R@3=0.00: The Executive's employment with the Company will commence on the Commencement Date and shall continue, subject to the remaining terms of this Agreement, until terminated by either party giving the other the following minimum advance written notice: 2.1.1 6 wee
  - top1: THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt 30772:31772 score=0.340: Agreement. The Executive waives any claim for innocent or negligent misrepresentation or negligent misstatement including in respect of any statement set out in this Agreement. 24.7 No variation or agreed termination of this Agreement shall be effective unless
  - doc_score=0.2974189074937808, top1=0.340, gap=0.036
- query: Consider the Service Agreement between Theravance Biopharma UK Limited and Brett Haumann; Can this contract be terminated for convenience, and under what conditions?
  - truth: THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt 18678:18997 R@3=0.00: The Company may, in its sole and absolute discretion, terminate the Executive's employment under this Agreement at any time and with immediate effect by notifying the Executive that the Company is exercising its right under this clause 17 and that it will make
  - top1: THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt 30772:31772 score=0.424: Agreement. The Executive waives any claim for innocent or negligent misrepresentation or negligent misstatement including in respect of any statement set out in this Agreement. 24.7 No variation or agreed termination of this Agreement shall be effective unless
  - doc_score=0.2974189074937808, top1=0.424, gap=0.001
- query: Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; Does this contract include an exclusivity agreement?
  - truth: DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt 5690:6079 R@3=0.00: Rubicon hereby grants to ISA during the Term (as defined below) and subject to the exclusions described in 2.4 below an exclusive, non-transferable license in the United States to market, sell, use, display, perform, sublicense and distribute the Rubicon Offer
  - top1: DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt 29243:29410 score=0.431: nd delivered by it, this Agreement will constitute a legal, valid and binding obligation of it, enforceable against it in accordance with this Agreement's provisions;
  - doc_score=0.36646911782307384, top1=0.431, gap=0.013

## lexical_mismatch (25)

- query: Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; What is the expiration date of this contract?
  - truth: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 5604:5739 R@3=0.00: The term of this Agreement shall be one (1) year unless terminated earlier in accordance with the terms of this Agreement (the "Term").
  - top1: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 17849:18849 score=0.338: 20. No Reliance No third party is entitled to rely on any of the representations, warranties and agreements contained in this Agreement. The Parties assume no liability to any third party because of any reliance on the representations, warranties and agreement
  - doc_score=0.48084359167195656, top1=0.338, gap=0.019
- query: Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; Is there an anti-assignment clause in this contract?
  - truth: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 17341:17432 R@3=0.00: The rights and obligations provided by this Agreement shall not be assignable by any Party.
  - top1: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 17849:18849 score=0.326: 20. No Reliance No third party is entitled to rely on any of the representations, warranties and agreements contained in this Agreement. The Parties assume no liability to any third party because of any reliance on the representations, warranties and agreement
  - doc_score=0.48084359167195656, top1=0.326, gap=0.006
- query: Consider the Service Agreement between Theravance Biopharma UK Limited and Brett Haumann; Is there a covenant not to sue included in this contract?
  - truth: THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt 27816:28397 R@3=0.00: If the Executive's employment is terminated at any time by reason of any reconstruction or amalgamation of any Group Company, whether by winding up or otherwise, and the Executive is offered employment with any concern or undertaking involved in or resulting f
  - top1: THERAVANCEBIOPHARMA,INC_05_08_2020-EX-10.2-SERVICE AGREEMENT.txt 31672:32513 score=0.405: onstitute one and the same agreement. 24.10 The Contracts (Rights of Third Parties) Act 1999 shall only apply to this Agreement in relation to any Group Company. No person other than the parties to this Agreement and any Group Company shall have any rights und
  - doc_score=0.2974189074937808, top1=0.405, gap=0.042
- query: Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; What is the governing law for this contract?
  - truth: DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt 36019:36116 R@3=0.00: This Agreement shall be governed by and interpreted under the laws of the State of Florida, USA,.
  - top1: DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt 29243:29410 score=0.442: nd delivered by it, this Agreement will constitute a legal, valid and binding obligation of it, enforceable against it in accordance with this Agreement's provisions;
  - doc_score=0.36646911782307384, top1=0.442, gap=0.023
- query: Consider the Strategic Alliance Agreement between Information System Associates, Inc. and Rubicon Software Group plc; Is there a clause preventing the solicitation of employees in this contract?
  - truth: DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt 21064:21193 R@3=0.00: Further, during the Non-Competition Period, Rubicon shall not solicit any employee of ISA or any employee of any ISA Client.
  - top1: DUOSTECHNOLOGIESGROUP,INC_04_21_2009-EX-10.1-STRATEGIC ALLIANCE AGREEMENT.txt 24743:25743 score=0.347: uch cause. Neither Party shall use all or any part of the Confidential Information of the other Party for any purpose other than to perform its obligations, or the exercise of such Party's rights and licenses, under this Agreement. Each Party shall (i) limit a
  - doc_score=0.36646911782307384, top1=0.347, gap=0.004
- query: Consider the Supply Agreement between Florida Chemical Company, LLC and Flotek Chemistry, LLC for Terpene Products; What is the governing law for this contract?
  - truth: FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt 17415:17518 R@3=0.00: This Agreement shall be governed by and construed in accordance with the laws of the state of Delaware.
  - top1: FLOTEKINDUSTRIESINCCN_05_09_2019-EX-10.1-SUPPLY AGREEMENT.txt 11168:12168 score=0.393: 16. Environmental Indemnity. Each party hereto agrees to comply with all applicable federal, state provincial and or local environmental law, ordinances, codes, rules, regulations and permits and to handle all raw materials, off specification product, excess o
  - doc_score=0.3536272634437956, top1=0.393, gap=0.050

## other_wrong_section (9)

- query: Consider the Service Agreement between BicycleTX Ltd and Nigel Crockett for Chief Business Officer Position; Does this contract include any right of first refusal, right of first offer, or right of first negotiation?
  - truth: BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt 6235:6531 R@3=0.00: On or as soon as practicable following the Effective Date, it is intended that you will be granted an option under the Option Plan to acquire 107,417 ordinary shares in the capital of BTL ("Shares") (representing approximately 0.6% of the Company's issued shar
  - top1: BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt 7939:8252 score=0.360: Any options granted under this paragraph 4.5 shall be subject to (i) the approval of the Board and/or the Compensation Committee; (ii) the rules of the Option Plan (as amended from time to time); and (iii) the terms of the option grant documentation which will
  - doc_score=0.3111064515889276, top1=0.360, gap=0.011
- query: Consider the Cooperation Agreement between HPIL ENERGYTECH Inc. and GINARES GROUP AG for Renewable Energy Projects; What is the governing law for this contract?
  - truth: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 16867:17117 R@3=0.00: This Agreement and its application and interpretation will be governed exclusively by its terms and the laws of the State of Nevada (USA), and excluding any conflicts of law provisions which would require the application of any law other than Nevada.
  - top1: HPILHOLDING_01_07_2015-EX-99.1-COOPERATION AGREEMENT.txt 18749:19749 score=0.394: , whether oral or written, of the Parties and there are no warranties, representations or other agreements between the Parties in connection with the subject matter hereof except as set forth specifically herein. No amendment, supplement, modification, waiver 
  - doc_score=0.48084359167195656, top1=0.394, gap=0.011
- query: Consider the Marketing and Transportation Services Agreement between Purolator Courier Ltd. and Parcelway Courier Systems Canada Ltd. (Dynamex Inc.); What is the expiration date of this contract?
  - truth: DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt 3307:3509 R@3=0.00: This Agreement shall be effective from the date first above written and shall continue indefinitely until terminated by either Party in accordance with the provisions of this Agreement.
  - top1: DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt 47546:48417 score=0.412: 32.1 In the event this Agreement is terminated pursuant to the provisions of paragraph 17, then the Party in default shall not enter into an agreement with any other Party to provide services similar to those provided herein or to provide its services similar 
  - doc_score=0.4587831459167665, top1=0.412, gap=0.032
- query: Consider the Co-Branding Agreement between PC Quote, Inc. and A.B. Watley, Inc. for Market Data Software; What is the governing law for this contract?
  - truth: PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding Agreement1.txt 14946:15133 R@3=0.00: This Agreement shall be interpreted, construed and enforced in all respects in accordance with the laws of the State of Illinois, except with regards to its rules regarding choice of law.
  - top1: PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding Agreement1.txt 16368:17008 score=0.407: A. The parties to this Agreement are independent contractors with requisite corporate power and authority to enter into this Agreement and carry out the transactions contemplated hereby. Neither party is a ABW or representative of the other party. Neither part
  - doc_score=0.3352138396612147, top1=0.407, gap=0.031
- query: Consider the Endorsement Agreement between ABG-Shaq, LLC and Papa John's International, Inc.; Is there an anti-assignment clause in this contract?
  - truth: PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt 34757:35166 R@3=0.00: In the event PAPA JOHN'S wishes to sub-contract any or all of the operation of the Products or its related business hereunder (e.g., design of the Products, advertising of the Products, creation of Products, etc.) to any third party (e.g., ad agencies, photogr
  - top1: PapaJohnsInternationalInc_20190617_8-K_EX-10.1_11707365_EX-10.1_Endorsement Agreement.txt 35637:35818 score=0.318: sure that all Sub-Contractors abide by the terms of this Agreement. All acts of all Sub-Contractors shall be deemed to be the acts of PAPA JOHN'S for all purposes of this Agreement.
  - doc_score=0.41980704458803214, top1=0.318, gap=0.015
- query: Consider the Walabot HOME Reseller Agreement between Vayyar Imaging Ltd. and Inde Living Holdings, Inc.; Is there an anti-assignment clause in this contract?
  - truth: HealthcareIntegratedTechnologiesInc_20190812_8-K_EX-10.1_11776966_EX-10.1_Reseller Agreement.txt 15974:16290 R@3=0.00: Supplier and/or Reseller may assign or novate this Agreement and the rights and obligations under it to any of its affiliates or upon any merger or acquisition or the sale of all or substantially all of its assets relating to the Agreement. Any purported assig
  - top1: HealthcareIntegratedTechnologiesInc_20190812_8-K_EX-10.1_11776966_EX-10.1_Reseller Agreement.txt 1800:2800 score=0.330: n Schedule 1. Appointment During the Term (defined below) and subject to the terms and conditions of this Agreement (including, but not limited to Section 12.4 hereof), Supplier hereby (i) appoints Reseller, and Reseller accepts the appointment, as a non‐ excl
  - doc_score=0.34003324533821744, top1=0.330, gap=0.018

## wrong_document (0)


## hallucinated_match (5)

- query: Consider the Marketing and Transportation Services Agreement between Purolator Courier Ltd. and Parcelway Courier Systems Canada Ltd. (Dynamex Inc.); Are limousine services provided to executives?
  - top1: DYNAMEXINC_06_06_1996-EX-10.4-TRANSPORTATION SERVICES AGREEMENT.txt 5393:6155 score=0.459: iii) In connection with such overnight service requests, will handle the customer request, will dispatch the pickup request to Purolator, will be responsible for billing the customer for the service and collecting the revenue and provide such sales and marketi
  - doc_score=0.4587831459167665, top1=0.459, gap=0.004
- query: Consider the Business Affiliate Agreement between Dr. George D. Green and UNION DENTAL CORP.; Can the affiliate promote the services on TikTok?
  - top1: UnionDentalHoldingsInc_20050204_8-KA_EX-10_3345577_EX-10_Affiliate Agreement.txt 1397:2264 score=0.420: 2. Services. It is anticipated that the Business Affiliate will provide services both for clients of the Business Affiliate and UDC that involve the use and disclosure of Confidential Information (the "Services"). Except as otherwise specified herein, the Part
  - doc_score=0.32773454288301807, top1=0.420, gap=0.038
- query: Does the agreement cover broadcast rights for the next Olympic Games?
  - top1: ArcGroupInc_20171211_8-K_EX-10.1_10976103_EX-10.1_Sponsorship Agreement.txt 14662:15662 score=0.359: all have the right to have its food products sold or otherwise distributed from the Stands and/or certain general concessions areas at the Stadium determined by Club or the Concessionaire. For purposes of clarity, nothing in this Agreement grants Sponsor the r
  - doc_score=None, top1=0.359, gap=0.006
- query: Does the contract mention a sabbatical policy for creative staff?
  - top1: BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt 42015:42553 score=0.358: 14.6 In the event that the Company exercises its rights and places you on Garden Leave under paragraph 10 above then the Restricted Period shall be reduced by any period/s spent by you on Garden Leave prior to the Termination Date. 14.7 During the Restricted P
  - doc_score=None, top1=0.358, gap=0.001
- query: What meal allowance is paid during a pandemic lockdown?
  - top1: BICYCLETHERAPEUTICSPLC_03_10_2020-EX-10.11-SERVICE AGREEMENT.txt 13391:14228 score=0.412: 9.3 Subject to your compliance with the Company's sickness absence procedures (as amended from time to time), the Company may in its sole and absolute discretion pay full salary and contractual benefits during any period of absence due to sickness or injury fo
  - doc_score=None, top1=0.412, gap=0.097
