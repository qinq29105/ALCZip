function decoder(input_file, bit_length)
    % LZW decoder function
    % Decompresses a file compressed using the LZW algorithm

    maximum_table_size = 2^bit_length;

    % Read compressed data from file
    fid = fopen(input_file, 'rb');
    compressed_data = fread(fid, 'uint16');
    fclose(fid);

    % Initialize the dictionary
    dictionary_size = 256;
    dictionary = containers.Map(num2cell(0:255), arrayfun(@char, 0:255, 'UniformOutput', false));
    next_code = 256;
    string = '';
    decompressed_data = '';

    % Decoding process
    for i = 1:length(compressed_data)
        code = compressed_data(i);

        if isKey(dictionary, code)
            entry = dictionary(code);
        elseif code == next_code
            entry = [string, string(1)];
        else
            error('Decoding failed: Unknown code %d', code);
        end

        decompressed_data = [decompressed_data, entry];

        if ~isempty(string)
            dictionary(next_code) = [string, entry(1)];
            next_code = next_code + 1;
        end

        string = entry;
    end

    % Write decompressed data to file
    [~, name, ~] = fileparts(input_file);
    output_file = strcat(name, '_decoded.txt');
    fid = fopen(output_file, 'w');
    fwrite(fid, decompressed_data, 'char');
    fclose(fid);
end

