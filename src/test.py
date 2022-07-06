import pandas as pd
import sys
import re
sys.path.insert(0, '../')
main = pd.read_csv('temp_master.csv')

#cols=list(main)
#cols.insert(0, cols.pop(cols.index('Season')))
#main.loc[:, cols]
main.insert(loc=SOME_INDEX, column="Offensive Play Style", value="")
main.insert(loc=SOME_INDEX, column="Defensive Play Style", value="")
for index, row in main.iterrows():
    position = row['Position 1']
    positions = re.split('/|-', position)
    main.loc[index, 'Position 1'] = positions[0]
    if len(positions) == 2:
        main.loc[index, 'Position 2'] = positions[1]
main.to_csv('temp_master.csv', index=False)
