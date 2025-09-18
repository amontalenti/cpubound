#!/usr/bin/env elixir

# Load the existing WordCounter module from wcdist.exs
Code.compile_file("wcdist.exs")

defmodule WordCountServer do
  def start do
    IO.puts("=" <> String.duplicate("=", 60))
    IO.puts("WORD COUNT SERVER STARTING")
    IO.puts("=" <> String.duplicate("=", 60))
    IO.puts("Server node: #{Node.self()}")
    IO.puts("Waiting for client connections...")
    IO.puts("")
    IO.puts("To connect from another machine, run:")
    IO.puts("  elixir client.exs")
    IO.puts("")
    IO.puts("Press Ctrl+C to stop the server")
    IO.puts("=" <> String.duplicate("=", 60))

    # Keep the server alive and monitor connections
    monitor_connections()
  end

  defp monitor_connections do
    receive do
      {:nodeup, node} ->
        IO.puts("✅ Client connected: #{node}")
        IO.puts("Connected nodes: #{inspect(Node.list())}")
        monitor_connections()

      {:nodedown, node} ->
        IO.puts("❌ Client disconnected: #{node}")
        IO.puts("Connected nodes: #{inspect(Node.list())}")
        monitor_connections()

      :stop ->
        IO.puts("Server shutting down...")
        System.halt(0)
    end
  end

  # Server just provides the node - clients handle the actual processing
end

# Start the server
WordCountServer.start()
