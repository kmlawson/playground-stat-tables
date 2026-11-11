# keyword rules for Financial Statement tables (title-based, order matters)
R=[('Police Deferred Pay',['insurance-and-pensions','police']),('Police Savings Bank',['savings-and-loans']),('Police Recreation',['recreation-and-amusements']),
('Police Secret Service',['police']),('Police Canteen',['police']),('Liquor-Sellers',['alcohol']),('Livery-Stable',['public-budgets']),
('Coolies',['postal-services']),('Post Office',['postal-services']),('Billiard and Bowling Saloons',['public-budgets']),('Nuisance Contractor',['public-health']),
('Volunteers',['militias-and-volunteer-forces']),('Town Band',['arts-and-music']),('Fire Department',['firefighting']),
('Municipal Loan',['public-debt']),('Sinking Fund',['public-debt']),('Expenditure — Interest',['public-debt']),('— Stud',['livestock']),('Water Supply',['water-and-sewerage']),
('Secretariat',['government-offices']),('Land and Buildings',['public-property']),('Land, Buildings',['public-property']),('Sanitary Branch',['public-health']),
('Trust Funds',['savings-and-loans']),('Bubbling Well',['police']),('Nuisance and Market',['public-health']),
('Land Tax',['taxation','land-tax']),('General Municipal Rate',['taxation','real-estate']),('Dues on Merch',['taxation']),
('License Fees',['taxation']),('Licence Fees',['taxation']),('Lock Hospital',['medical-services']),('Night-soil',['public-health']),
('Relief of Poor',['poor-relief']),('Hospitals',['medical-services']),('Sanitary — Medical',['medical-services']),('Market and Nuisance',['public-health']),
('Telephone',['telephone']),('Outside Roads',['roads-and-bridges']),('Public Garden',['recreation-and-amusements']),
('Bridges',['roads-and-bridges']),('Buildings',['construction']),('Drainage',['water-and-sewerage']),('Landing-Stages',['ports']),
('Bundings',['river-conservancy']),('Fire-Wells',['firefighting']),('Creeks',['river-conservancy']),('Latrines',['public-health']),
('Widening',['roads-and-bridges']),('Roads',['roads-and-bridges']),('Museum',['museums-and-heritage']),('Library',['libraries']),
('Education',['education-finance']),('Fees and Expenses on Land',['land-registration']),('Lighting',['gas']),('Police',['police']),('Cemeteries',['public-budgets']),('Interest',['public-budgets'])]
TOP={'insurance-and-pensions':'crime-and-justice','postal-services':'communications','militias-and-volunteer-forces':'military','arts-and-music':'culture','public-debt':'finance','government-offices':'government','public-health':'health','livestock':'agriculture','alcohol':'manufacturing','police':'crime-and-justice','medical-services':'health','public-health':'health','poor-relief':'welfare','telephone':'communications',
'roads-and-bridges':'transportation','ports':'transportation','construction':'utilities','water-and-sewerage':'utilities','river-conservancy':'utilities',
'gas':'utilities','firefighting':'disasters','recreation-and-amusements':'culture','museums-and-heritage':'culture','libraries':'culture','education-finance':'education'}
def fin(title):
  t=title.replace('—','—')
  for k,tg in R:
    if k in t:
      tg=tg+(['public-budgets'] if 'public-budgets' not in tg and tg[0] not in ('taxation',) else [])
      tp=['finance']
      if tg[0] in TOP: tp.append(TOP[tg[0]])
      tp=list(dict.fromkeys(tp));return (tp,tg[:3],[],'financial statement: '+k)
  return (['finance'],['public-budgets'],[],'financial statement carried forward / subtotal')
