#!/usr/bin/env elixir

defmodule WordCounter do
  def count_words(text_chunk) do
    Enum.reduce(text_chunk, %{}, fn word, counts ->
      # Simulate the MD5 hash computation from the Python version
      :crypto.hash(:md5, word) |> Base.encode16(case: :lower)
      Map.update(counts, word, 1, &(&1 + 1))
    end)
  end

  def merge_counts(count_dicts) do
    Enum.reduce(count_dicts, %{}, fn dict, result ->
      Map.merge(result, dict, fn _key, v1, v2 -> v1 + v2 end)
    end)
  end

  def generate_text(words, count) do
    1..count
    |> Enum.map(fn _ -> Enum.random(words) end)
  end

  def run do
    words = [
      "hello", "world", "elixir", "parallel", "cpu", "cores", "process", "actor",
      "data", "algorithm", "benchmark", "performance", "memory", "cache", "loop",
      "function", "variable", "string", "integer", "float", "boolean", "list"
    ]

    IO.puts("Generating large dataset...")
    text = generate_text(words, 100_000_000)  # 100M words

    IO.puts("Processing #{length(text) |> :erlang.integer_to_binary() |> String.replace(~r/(\d)(?=(\d{3})+$)/, "\\1,")} words across all CPU cores...")

    # Split into chunks for parallel processing
    chunk_size = 50_000
    chunks = Enum.chunk_every(text, chunk_size)
    IO.puts("Split into #{length(chunks)} chunks of #{chunk_size} words each")

    # Use Task.async_stream for parallel processing - this leverages Elixir's actor model
    word_counts =
      chunks
      |> Task.async_stream(&count_words/1, max_concurrency: System.schedulers_online())
      |> Enum.map(fn {:ok, result} -> result end)

    # Merge results
    final_counts = merge_counts(word_counts)

    # Print results
    final_counts
    |> Enum.sort_by(fn {word, _count} -> word end)
    |> Enum.each(fn {word, count} -> IO.puts("#{word}: #{count}") end)
  end
end

WordCounter.run()