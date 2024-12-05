% Project Implementation for LZW Encoding and Decoding
close all;
clear;
clc;

%% Input Parameters
file_path = './GameofThrones.txt'; % Specify the input file path
bit_length = 10; % Specify the bit length for the dictionary

%% Compress process
disp('Starting encoding...');
tic;  % Start timer for encoding
[compressed_data, dictionary, char_probabilities] = encoder(file_path, bit_length);
compressed_file = strcat(file_path(1:end-4), '.lzw');
write_compressed_file(compressed_file, compressed_data);
encoding_time = toc;  % Stop timer and capture encoding time

% Calculate Compression Ratio
compression_ratio = calculate_compression_ratio(file_path, compressed_file);

% Display Encoding Results
fprintf('Encoding completed!\n');
fprintf('Encoding time: %.4f seconds\n', encoding_time);
fprintf('Compression ratio: %.2f%%\n', compression_ratio);

% Calculate and Display Encoding Statistics
[len, ave, HX, efficiency, r] = calculate_statistics(char_probabilities, bit_length, compressed_data);
fprintf('Average Codeword Length: %f\n', ave);
fprintf('Source Entropy: %f\n', HX);
fprintf('Encoding Efficiency: %f\n', efficiency);
fprintf('Redundancy: %f\n', r);


%% Decoding Process
disp('Starting decoding...');
tic;  % Start timer for decoding
decoder(compressed_file, bit_length);
decoding_time = toc;  % Stop timer and capture decoding time
disp('Decoding completed!');
fprintf('Decoding time: %.4f seconds\n', decoding_time);



%% function
function write_compressed_file(output_file, compressed_data)
    % Writes the compressed data to a binary file
    fid = fopen(output_file, 'wb');
    fwrite(fid, compressed_data, 'uint16');
    fclose(fid);
end

function compression_ratio = calculate_compression_ratio(original_file, compressed_file)
    % Calculates the compression ratio
    original_info = dir(original_file);
    compressed_info = dir(compressed_file);
    original_size = original_info.bytes;
    compressed_size = compressed_info.bytes;
    fprintf('Original file size: %d bytes\n', original_size);
    fprintf('Compressed file size: %d bytes\n', compressed_size);
    compression_ratio = (compressed_size / original_size) * 100;
end

function [len, ave, HX, efficiency, r] = calculate_statistics(prob, bit_length, compressed_data)
    % Statistical analysis function: Calculate encoding efficiency and other parameters
    % prob: Character probability distribution
    % bit_length: Maximum codeword length for LZW (dictionary size)
    % compressed_data: The compressed data

    % Source entropy H(X)
    HX = -sum(prob .* log2(prob));

    % Actual codeword lengths
    codeword_lengths = ceil(log2(compressed_data + 1)); % Dynamic codeword length
    ave = mean(codeword_lengths); % Average codeword length

    % Encoding efficiency
    efficiency = HX / ave;

    % Redundancy
    r = 1 - efficiency;

    % Return values
    len = codeword_lengths; % Length of each codeword
end

