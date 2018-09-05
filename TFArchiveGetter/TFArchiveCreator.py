import pandas


class TFArchiveCreator:

    def __init__(self, output_file):
        self.__output_file = output_file

    def create(self, df):
        df.to_csv(self.__output_file, index=False)

    def add_new_row(self, day, row):

        arch_df = pandas.read_csv(self.__output_file, index_col='date')
        arch_df.loc[day.strftime('%Y-%m-%d')] = [row[0], row[1], row[2], row[3]]
        new_index = [day.strftime('%Y-%m-%d')] + [ind for ind in arch_df.index if ind != day.strftime('%Y-%m-%d')]
        arch_df = arch_df.reindex(index=new_index)
        arch_df['date'] = arch_df.index

        arch_df.to_csv(self.__output_file, index=False)
