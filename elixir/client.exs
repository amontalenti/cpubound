#!/usr/bin/env elixir

# Load the existing WordCounter module from wcdist.exs
Code.compile_file("wcdist.exs")

defmodule WordCountClient do
  def run do
    IO.puts("=" <> String.duplicate("=", 60))
    IO.puts("WORD COUNT CLIENT STARTING")
    IO.puts("=" <> String.duplicate("=", 60))

    # Try to connect to server
    server_node = get_server_node()

    case Node.connect(server_node) do
      true ->
        IO.puts("✅ Connected to server: #{server_node}")
        IO.puts("Client node: #{Node.self()}")
        IO.puts("Connected nodes: #{inspect(Node.list())}")
        IO.puts("")
        run_distributed_word_count()

      false ->
        IO.puts("❌ Failed to connect to server: #{server_node}")
        IO.puts("Make sure the server is running on your Mac")
        System.halt(1)
    end
  end

  defp get_server_node do
    # Try to get server node from command line args or environment
    case System.argv() do
      [server_name] -> String.to_atom(server_name)
      [] ->
        # Default server node (replace with your Mac's IP)
        :"mike@192.168.86.21"
    end
  end

  defp run_distributed_word_count do
    words = [
      "hello", "world", "elixir", "parallel", "cpu", "cores", "process", "actor",
      "data", "algorithm", "benchmark", "performance", "memory", "cache", "loop",
      "function", "variable", "string", "integer", "float", "boolean", "list"
    ]

    IO.puts("Generating large dataset...")
    text = generate_text(words, 100_000_000)  # 100M words

    IO.puts("Processing #{format_number(length(text))} words across all CPU cores...")

    # Split into chunks for parallel processing
    chunk_size = 50_000
    chunks = Enum.chunk_every(text, chunk_size)
    IO.puts("Split into #{length(chunks)} chunks of #{chunk_size} words each")

    # Use Task.Supervisor for cluster-capable parallel processing
    {:ok, supervisor} = Task.Supervisor.start_link()

    available_nodes = [node() | Node.list()]
    IO.puts("Available nodes: #{inspect(available_nodes)}")

    # Distribute chunks evenly across nodes
    chunk_assignments = distribute_chunks_to_nodes(chunks, available_nodes)

    IO.puts("")
    IO.puts("Starting distributed processing...")
    start_time = System.monotonic_time(:millisecond)

    word_counts =
      chunk_assignments
      |> Enum.map(fn {node, node_chunks} ->
        if node == node() do
          # Process locally
          Task.async(fn ->
            node_chunks
            |> Enum.map(&WordCounter.count_words/1)
            |> WordCounter.merge_counts()
          end)
        else
          # Process on remote node (server) - send individual chunks
          Task.async(fn ->
            node_chunks
            |> Enum.map(fn chunk ->
              case :rpc.call(node, WordCounter, :count_words, [chunk]) do
                result when is_map(result) -> result
                error ->
                  IO.puts("Error processing chunk on #{node}: #{inspect(error)}")
                  %{}
              end
            end)
            |> WordCounter.merge_counts()
          end)
        end
      end)
      |> Enum.map(&Task.await(&1, 30_000))

    end_time = System.monotonic_time(:millisecond)
    processing_time = (end_time - start_time) / 1000

    # Merge results
    final_counts = WordCounter.merge_counts(word_counts)

    IO.puts("")
    IO.puts("=" <> String.duplicate("=", 60))
    IO.puts("RESULTS")
    IO.puts("=" <> String.duplicate("=", 60))
    IO.puts("Processing time: #{Float.round(processing_time, 2)} seconds")
    IO.puts("Words per second: #{Float.round(length(text) / processing_time, 2)}")
    IO.puts("Chunks per second: #{Float.round(length(chunks) / processing_time, 2)}")
    IO.puts("")
    IO.puts("Word counts:")

    # Print results
    final_counts
    |> Enum.sort_by(fn {word, _count} -> word end)
    |> Enum.each(fn {word, count} -> IO.puts("#{word}: #{count}") end)

    Task.Supervisor.stop(supervisor)
  end

  def generate_text(words, count) do
    1..count
    |> Enum.map(fn _ -> Enum.random(words) end)
  end

  defp distribute_chunks_to_nodes(chunks, nodes) do
    chunks
    |> Enum.with_index()
    |> Enum.group_by(fn {_chunk, index} ->
      Enum.at(nodes, rem(index, length(nodes)))
    end)
    |> Enum.map(fn {node, chunk_index_pairs} ->
      node_chunks = Enum.map(chunk_index_pairs, fn {chunk, _index} -> chunk end)
      {node, node_chunks}
    end)
  end

  defp format_number(number) do
    number
    |> Integer.to_string()
    |> String.reverse()
    |> String.graphemes()
    |> Enum.chunk_every(3)
    |> Enum.map(&Enum.reverse/1)
    |> Enum.map(&Enum.join/1)
    |> Enum.join(",")
    |> String.reverse()
  end
end

# Run the client
WordCountClient.run()
