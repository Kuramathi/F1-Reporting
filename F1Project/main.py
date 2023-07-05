from src.reporting import readcsv, data_conversation, printing

FILENAME = "data/constructors.csv"
ENCODING = "utf-8"
DELIMITER = ","


def main() -> None:
    df = readcsv(FILENAME, DELIMITER, ENCODING)

    for column in df.columns:
        data, datatype = data_conversation(df[column])

        dataset = data.dropna()
        sparsity = 1.0 - len(dataset) / len(dataset[column])
        print(sparsity)

        printing(data, column, datatype)


if __name__ == '__main__':
    main()
