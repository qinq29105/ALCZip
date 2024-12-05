function [compressed_data, dictionary, char_probabilities] = encoder(input_file, bit_length)
    % LZW encoder function
    % Compresses the input file using the LZW algorithm and computes character probabilities

    maximum_table_size = 2^bit_length;

    % Read input file content
    fid = fopen(input_file, 'r');
    data = fread(fid, '*char')';
    fclose(fid);

    % Calculate character probabilities
    unique_chars = unique(data);
    char_counts = histcounts(double(data), [double(unique_chars), inf]);
    char_probabilities = char_counts / sum(char_counts);

    % Initialize the dictionary
    dictionary_size = 256;
    dictionary = containers.Map(arrayfun(@char, 0:255, 'UniformOutput', false), num2cell(0:255));
    string = '';
    compressed_data = [];

    % Encoding process
    for i = 1:length(data)
        symbol = data(i);
        string_plus_symbol = [string, symbol];

        if isKey(dictionary, string_plus_symbol)
            string = string_plus_symbol;
        else
            compressed_data = [compressed_data; dictionary(string)];
            if length(dictionary) < maximum_table_size
                dictionary(string_plus_symbol) = dictionary_size;
                dictionary_size = dictionary_size + 1;
            end
            string = symbol;
        end
    end

    % Add the final string to the compressed data
    if ~isempty(string)
        compressed_data = [compressed_data; dictionary(string)];
    end
end
