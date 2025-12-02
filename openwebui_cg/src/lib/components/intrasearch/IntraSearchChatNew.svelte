<script lang="ts">
	import { onMount } from 'svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';

	export let chatIdProp: string;

	let query = '';
	let messages: Array<{
		id: string;
		role: 'user' | 'assistant';
		content: string;
		timestamp: Date;
		results?: any[];
	}> = [];
	let isSearching = false;
	let searchStatus = '';
	let aiResponse = '';

	const suggestionCards = [
		{ title: 'Company policies', subtitle: 'Search internal policies' },
		{ title: 'HR documents', subtitle: 'Employee resources' },
		{ title: 'Technical docs', subtitle: 'API & system guides' },
		{ title: 'Team contacts', subtitle: 'Directory & org chart' }
	];

	async function performSearch() {
		if (!query.trim() || isSearching) return;

		isSearching = true;
		searchStatus = 'Initializing search...';
		aiResponse = '';

		const userMessage = {
			id: crypto.randomUUID(),
			role: 'user' as const,
			content: query,
			timestamp: new Date()
		};

		messages = [userMessage];
		const currentQuery = query;

		try {
			const response = await fetch(`${WEBUI_API_BASE_URL}/intrasearch/search`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				credentials: 'include',
				body: JSON.stringify({
					query: currentQuery,
					max_results: 10,
					search_depth: 'detailed',
					include_attachments: true,
					stream: true
				})
			});

			if (!response.ok) {
				throw new Error(`Search failed: ${response.statusText}`);
			}

			// Handle streaming response
			const reader = response.body?.getReader();
			const decoder = new TextDecoder();
			let buffer = '';
			let sources: any[] = [];

			if (reader) {
				while (true) {
					const { done, value } = await reader.read();
					if (done) break;

					buffer += decoder.decode(value, { stream: true });
					const lines = buffer.split('\n');
					buffer = lines.pop() || '';

					for (const line of lines) {
						if (line.startsWith('data: ')) {
							const data = line.slice(6);
							if (data === '[DONE]') break;

							try {
								const event = JSON.parse(data);

								switch (event.type) {
									case 'status':
										searchStatus = event.message;
										break;
									case 'ai_start':
										searchStatus = 'Generating response...';
										break;
									case 'ai_chunk':
										aiResponse += event.content;
										break;
									case 'ai_end':
										searchStatus = 'Gathering sources...';
										break;
									case 'source':
										sources.push(event.file);
										break;
									case 'complete':
										searchStatus = `Completed in ${event.search_time_ms}ms`;
										break;
									case 'error':
										throw new Error(event.message);
								}
							} catch (e) {
								console.error('Failed to parse event:', e);
							}
						}
					}
				}
			}

			// Create assistant message with AI response and sources
			const assistantMessage = {
				id: crypto.randomUUID(),
				role: 'assistant' as const,
				content: aiResponse || `Search completed`,
				timestamp: new Date(),
				results: [
					{
						id: 'ai_answer',
						title: 'Analysis',
						content: aiResponse,
						source: 'AI-Generated',
						score: 1.0,
						metadata: { document_type: 'analysis' }
					},
					...sources.map((source, idx) => ({
						id: source.id,
						title: source.name,
						content: `View document in Google Drive`,
						source: 'Google Drive',
						score: 0.95 - (idx * 0.05),
						metadata: {
							document_type: 'document',
							url: source.url
						}
					}))
				]
			};

			messages = [...messages, assistantMessage];
		} catch (error) {
			console.error('Search error:', error);
			const errorMessage = {
				id: crypto.randomUUID(),
				role: 'assistant' as const,
				content: `Error performing search: ${error.message}`,
				timestamp: new Date()
			};
			messages = [...messages, errorMessage];
		} finally {
			isSearching = false;
			searchStatus = '';
		}
	}

	function handleSuggestionClick(suggestionTitle: string) {
		query = suggestionTitle;
		performSearch();
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			performSearch();
		}
	}
</script>

<style>
	@keyframes spin {
		from {
			transform: rotate(0deg);
		}
		to {
			transform: rotate(360deg);
		}
	}

	.spinner {
		animation: spin 1s linear infinite;
	}

	.pulse-slow {
		animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
</style>

<div class="w-full">
	<div class="flex flex-col items-center {messages.length === 0 ? 'justify-center min-h-screen' : 'pt-8'} px-4 transition-all duration-500 ease-in-out">

		<div class="text-center mb-8 {messages.length > 0 ? 'scale-75 origin-top mb-4' : ''} transition-all">
			<h1 class="text-3xl font-semibold text-gray-900 dark:text-white tracking-tight">
				Enterprise Internal Systems Search
			</h1>
			<p class="mt-3 text-base text-gray-500 dark:text-gray-400">
				Search across your company's internal documents, knowledge base, and databases
			</p>
		</div>

		<div class="w-full max-w-3xl relative z-10">
			<div class="relative group">
				<input
					type="text"
					bind:value={query}
					on:keydown={handleKeydown}
					disabled={isSearching}
					placeholder="How can I help you search today?"
					class="w-full h-14 pl-6 pr-12 rounded-full border border-gray-200 shadow-[0_2px_5px_-1px_rgba(0,0,0,0.1)] focus:shadow-lg focus:border-gray-300 focus:outline-none text-gray-700 text-lg placeholder-gray-400 transition-shadow dark:bg-gray-800 dark:border-gray-700 dark:text-white dark:placeholder-gray-500 disabled:opacity-50"
				/>
				<button
					class="absolute right-4 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
					aria-label="Voice search"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
						<path stroke-linecap="round" stroke-linejoin="round" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
					</svg>
				</button>
			</div>

			<!-- Spinner Loader con Favicon -->
			{#if isSearching}
				<div class="mt-8 flex flex-col items-center justify-center py-8">
					<div class="relative">
						<img
							src="/favicon.svg"
							alt="Loading"
							class="w-16 h-16 spinner opacity-80"
						/>
					</div>
					<p class="mt-4 text-sm text-gray-600 dark:text-gray-400 pulse-slow">
						{searchStatus || 'Searching...'}
					</p>
				</div>
			{/if}
		</div>

		{#if messages.length === 0 && !isSearching}
			<div class="mt-12 w-full max-w-3xl animate-in fade-in slide-in-from-bottom-4 duration-500">
				<div class="flex justify-center mb-4">
					<span class="text-xs font-medium text-gray-400 uppercase tracking-wider">+ Suggested</span>
				</div>

				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					{#each suggestionCards as card}
						<button
							on:click={() => handleSuggestionClick(card.title)}
							class="flex flex-col items-start p-4 rounded-xl border border-gray-100 bg-white hover:border-gray-200 hover:shadow-md transition-all text-left group dark:bg-gray-800 dark:border-gray-700 dark:hover:border-gray-600"
						>
							<span class="font-bold text-gray-800 group-hover:text-blue-600 dark:text-gray-200 dark:group-hover:text-blue-400 transition-colors">
								{card.title}
							</span>
							<span class="text-sm text-gray-500 mt-1 dark:text-gray-400">
								{card.subtitle}
							</span>
						</button>
					{/each}
				</div>
			</div>

		{:else if messages.length > 0 && !isSearching}
			<div class="w-full max-w-4xl mt-8 pb-10 overflow-y-auto">
				{#each messages as message}
					{#if message.role === 'assistant' && message.results}
						<div class="space-y-4">
							{#each message.results as result}
								<div class="group block p-5 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-sm transition-all dark:bg-gray-800 dark:border-gray-700">
									<div class="flex items-start">
										<div class="flex-1">
											<!-- Clean header without badges -->
											<div class="flex items-center gap-2 mb-1">
												<span class="text-xs text-gray-500 dark:text-gray-400">{result.source}</span>
											</div>

											<!-- Title -->
											<h3 class="text-base font-medium text-gray-900 dark:text-gray-100 mb-2">
												{#if result.metadata?.url}
													<a href={result.metadata.url} target="_blank" class="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">{result.title}</a>
												{:else}
													{result.title}
												{/if}
											</h3>

											<!-- Content -->
											<p class="text-sm text-gray-700 leading-relaxed dark:text-gray-300 whitespace-pre-wrap">
												{result.content}
											</p>
										</div>
									</div>
								</div>
							{/each}
						</div>
					{:else if message.role === 'assistant' && !message.results}
						<div class="p-4 rounded-lg bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800">
							{message.content}
						</div>
					{/if}
				{/each}
			</div>
		{/if}
	</div>
</div>
