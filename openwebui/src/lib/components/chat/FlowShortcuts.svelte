<script lang="ts">
	/**
	 * Model Shortcuts Component
	 *
	 * Displays a configurable grid of shortcut cards for quick model selection.
	 * Features include:
	 * - Multiple grid layouts (2x2, 3x3, 4x2)
	 * - Drag-and-drop reordering with svelte-dnd-action
	 * - Edit mode for managing shortcuts
	 * - Modal for creating/editing shortcuts
	 *
	 * @prop {Function} onSelect - Callback when shortcut is clicked (receives prompt and options)
	 * @prop {Function} onModelChange - Callback to change selected models
	 * @prop {string[]} selectedModels - Currently selected models (inherited from chat)
	 */

	import { onMount, getContext } from 'svelte';
	import { fade } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import { dndzone, TRIGGERS, SHADOW_PLACEHOLDER_ITEM_ID } from 'svelte-dnd-action';
	import { settings, models } from '$lib/stores';
	import { updateUserSettings, getUserSettings } from '$lib/apis/users';
	import { toast } from 'svelte-sonner';

	import ShortcutCard from './ShortcutCard.svelte';
	import AddShortcutModal from './AddShortcutModal.svelte';

	const i18n = getContext('i18n');

	// Props
	export let onSelect: (prompt: string, options?: { autoSubmit?: boolean }) => void = () => {};
	export let onModelChange: (modelIds: string[]) => void = () => {};
	export let selectedModels: string[] = [];

	// State
	let shortcuts: any[] = [];
	let editMode = false;
	let showAddModal = false;
	let editingShortcut: any = null;
	let preselectedModelId: string | null = null;
	let loading = true;

	// DnD state
	let dragDisabled = true;
	let flipDurationMs = 200;

	// Settings
	$: flowShortcutsEnabled = $settings?.ui?.flowShortcuts?.enabled ?? true;
	$: layout = $settings?.ui?.flowShortcuts?.layout ?? '2x2';

	// Grid columns based on layout
	$: gridCols = (() => {
		switch (layout) {
			case '3x3':
				return 'grid-cols-3';
			case '4x2':
				return 'grid-cols-4';
			case '2x2':
			default:
				return 'grid-cols-2';
		}
	})();

	// Calculate visible shortcuts
	$: maxVisible = (() => {
		switch (layout) {
			case '3x3':
				return 9;
			case '4x2':
				return 8;
			case '2x2':
			default:
				return 4;
		}
	})();

	// Visible shortcuts (filtered and limited)
	$: visibleShortcuts = shortcuts
		.filter((s) => s.enabled !== false)
		.sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
		.slice(0, maxVisible);

	// Load shortcuts from settings
	const loadShortcuts = async () => {
		try {
			loading = true;
			console.log('🔍 [FlowShortcuts] Loading shortcuts...');

			// Always fetch from API instead of store to ensure fresh data
			const token = localStorage.token;
			if (!token) {
				console.warn('⚠️ [FlowShortcuts] No auth token');
				shortcuts = [];
				return;
			}

			// Fetch fresh settings from API
			const freshSettings = await getUserSettings(token);
			console.log('📋 [FlowShortcuts] Fresh settings from API:', freshSettings?.ui?.flowShortcuts);

			// Get shortcuts from fresh settings
			const settingsShortcuts = freshSettings?.ui?.flowShortcuts?.shortcuts ?? [];

			if (Array.isArray(settingsShortcuts)) {
				shortcuts = settingsShortcuts.map((s, idx) => ({
					...s,
					id: s.id || crypto.randomUUID(),
					order: s.order ?? idx
				}));
				console.log('✅ [FlowShortcuts] Loaded', shortcuts.length, 'shortcuts');
			} else {
				console.warn('⚠️ [FlowShortcuts] Invalid shortcuts data:', settingsShortcuts);
				shortcuts = [];
			}
		} catch (error) {
			console.error('❌ [FlowShortcuts] Failed to load shortcuts:', error);
			shortcuts = [];
		} finally {
			loading = false;
		}
	};


	// Save shortcuts to settings
	const saveShortcuts = async (updatedShortcuts: any[]) => {
		try {
			console.log('💾 [FlowShortcuts] Saving shortcuts...', updatedShortcuts.length);

			const token = localStorage.token;
			if (!token) {
				throw new Error('No auth token');
			}

			// Fetch fresh settings first to avoid overwriting other data
			const freshSettings = await getUserSettings(token);

			const updatedSettings = {
				...freshSettings,
				ui: {
					...freshSettings?.ui,
					flowShortcuts: {
						...freshSettings?.ui?.flowShortcuts,
						shortcuts: updatedShortcuts
					}
				}
			};

			await updateUserSettings(token, updatedSettings);

			// Update local store
			settings.set(updatedSettings);

			console.log('✅ [FlowShortcuts] Shortcuts saved');
		} catch (error) {
			console.error('❌ [FlowShortcuts] Failed to save shortcuts:', error);
			toast.error('Failed to save shortcuts');
			throw error;
		}
	};

	// Handle shortcut click
	const handleShortcutClick = (shortcut: any) => {
		if (editMode) return;

		console.log('🖱️ [ModelShortcuts] Shortcut clicked:', shortcut.title);

		// Change to selected model (single model)
		if (shortcut.modelId) {
			onModelChange([shortcut.modelId]);

			// Visual feedback: Show toast with model name
			const modelName = $models.find(m => m.id === shortcut.modelId)?.name || shortcut.modelId;
			toast.success(`${shortcut.icon} Switched to ${modelName}`);
		}

		// Optionally fill prompt - FIXED: Pass correct format {type, data, autoSubmit}
		if (shortcut.prompt) {
			onSelect({
				type: 'prompt',
				data: shortcut.prompt,
				autoSubmit: shortcut.autoSubmit
			});
		}
	};

	// Handle edit shortcut
	const handleEditShortcut = (shortcut: any) => {
		console.log('✏️ [ModelShortcuts] Editing shortcut:', shortcut.id);
		editingShortcut = shortcut;
		preselectedModelId = null;
		showAddModal = true;
	};

	// Handle delete shortcut
	const handleDeleteShortcut = async (shortcut: any) => {
		const confirmed = confirm(`Delete "${shortcut.title}"?`);
		if (!confirmed) return;

		console.log('🗑️ [FlowShortcuts] Deleting shortcut:', shortcut.id);

		try {
			const updatedShortcuts = shortcuts.filter((s) => s.id !== shortcut.id);
			await saveShortcuts(updatedShortcuts);
			shortcuts = updatedShortcuts;
			toast.success('Shortcut deleted');
		} catch (error) {
			console.error('❌ [FlowShortcuts] Failed to delete shortcut:', error);
		}
	};

	// Handle add new shortcut
	const handleAddShortcut = () => {
		console.log('➕ [ModelShortcuts] Opening add modal');
		editingShortcut = null;
		preselectedModelId = null;
		showAddModal = true;
	};

	// Handle modal close
	const handleModalClose = () => {
		console.log('🚪 [ModelShortcuts] Closing modal');
		showAddModal = false;
		editingShortcut = null;
		preselectedModelId = null;
		// Reload shortcuts to reflect any changes
		loadShortcuts();
	};

	// DnD handlers
	const handleDndConsider = (e: CustomEvent) => {
		shortcuts = e.detail.items;
	};

	const handleDndFinalize = async (e: CustomEvent) => {
		shortcuts = e.detail.items;

		// Update order based on new positions
		const reorderedShortcuts = shortcuts.map((s, idx) => ({
			...s,
			order: idx
		}));

		// Save to API with debounce
		try {
			await saveShortcuts(reorderedShortcuts);
			shortcuts = reorderedShortcuts;
			console.log('✅ [FlowShortcuts] Reorder saved');
		} catch (error) {
			console.error('❌ [FlowShortcuts] Failed to save reorder:', error);
		}
	};

	// Toggle edit mode
	const toggleEditMode = () => {
		editMode = !editMode;
		dragDisabled = !editMode;
		console.log('🔧 [FlowShortcuts] Edit mode:', editMode);
	};

	// Initialize
	onMount(() => {
		loadShortcuts();
	});

	// Watch for settings changes (e.g., from another tab)
	$: if ($settings?.ui?.flowShortcuts?.shortcuts) {
		const settingsShortcuts = $settings.ui.flowShortcuts.shortcuts;
		if (Array.isArray(settingsShortcuts) && !loading) {
			// Only update if different to avoid loops
			const currentIds = shortcuts.map((s) => s.id).join(',');
			const newIds = settingsShortcuts.map((s: any) => s.id).join(',');
			if (currentIds !== newIds) {
				console.log('🔄 [FlowShortcuts] Settings changed, reloading...');
				loadShortcuts();
			}
		}
	}
</script>

{#if flowShortcutsEnabled}
	<div class="flow-shortcuts-container mb-4" in:fade={{ duration: 200 }}>
		<!-- Header with Edit Toggle -->
		<div class="flex items-center justify-between mb-3">
			<h3 class="text-sm font-medium text-gray-600 dark:text-gray-400">
				{$i18n.t('Quick Shortcuts')}
			</h3>
			<div class="flex items-center gap-2">
				{#if editMode}
					<button
						on:click={handleAddShortcut}
						class="text-xs px-2 py-1 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 hover:bg-blue-200 dark:hover:bg-blue-900/50 transition"
					>
						+ {$i18n.t('Add')}
					</button>
				{/if}
				<button
					on:click={toggleEditMode}
					class="text-xs px-2 py-1 rounded transition"
					class:bg-gray-100={!editMode}
					class:dark:bg-gray-700={!editMode}
					class:text-gray-600={!editMode}
					class:dark:text-gray-400={!editMode}
					class:bg-blue-100={editMode}
					class:dark:bg-blue-900={editMode}
					class:text-blue-600={editMode}
					class:dark:text-blue-400={editMode}
				>
					{editMode ? $i18n.t('Done') : $i18n.t('Edit')}
				</button>
			</div>
		</div>

		<!-- Shortcuts Grid -->
		{#if loading}
			<div class="grid {gridCols} gap-3">
				{#each Array(maxVisible) as _, i}
					<div
						class="animate-pulse bg-gray-100 dark:bg-gray-800 rounded-xl h-36"
					></div>
				{/each}
			</div>
		{:else if visibleShortcuts.length === 0}
			<div class="text-center py-8 text-gray-500 dark:text-gray-400">
				{#if editMode}
					<p class="mb-2">{$i18n.t('No shortcuts yet')}</p>
					<button
						on:click={handleAddShortcut}
						class="text-blue-600 dark:text-blue-400 hover:underline"
					>
						{$i18n.t('Create your first shortcut')}
					</button>
				{:else}
					<p>{$i18n.t('No shortcuts configured')}</p>
					<p class="text-xs mt-1">{$i18n.t('Click Edit to add shortcuts')}</p>
				{/if}
			</div>
		{:else}
			<div
				class="grid {gridCols} gap-3"
				use:dndzone={{
					items: visibleShortcuts,
					flipDurationMs,
					dragDisabled,
					dropTargetStyle: {},
					type: 'shortcuts'
				}}
				on:consider={handleDndConsider}
				on:finalize={handleDndFinalize}
			>
				{#each visibleShortcuts.filter(s => s.id !== SHADOW_PLACEHOLDER_ITEM_ID) as shortcut, idx (shortcut.id)}
					<div
						class="shortcut-item"
						animate:flip={{ duration: flipDurationMs }}
					>
						<ShortcutCard
							{shortcut}
							{idx}
							{editMode}
							onClick={() => handleShortcutClick(shortcut)}
							onEdit={() => handleEditShortcut(shortcut)}
							onDelete={() => handleDeleteShortcut(shortcut)}
						/>
					</div>
				{/each}
			</div>
		{/if}

		<!-- Add Shortcut Button - IMPROVED: More visible and prominent -->
		{#if !editMode && visibleShortcuts.length > 0 && visibleShortcuts.length < maxVisible}
			<div class="mt-4 text-center">
				<button
					on:click={() => {
						editMode = true;
						handleAddShortcut();
					}}
					class="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-lg transition-all border-2 border-dashed border-blue-300 dark:border-blue-600 bg-blue-50 dark:bg-blue-900/10 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/20 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-md"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 20 20"
						fill="currentColor"
						class="w-5 h-5"
					>
						<path
							d="M10.75 4.75a.75.75 0 0 0-1.5 0v4.5h-4.5a.75.75 0 0 0 0 1.5h4.5v4.5a.75.75 0 0 0 1.5 0v-4.5h4.5a.75.75 0 0 0 0-1.5h-4.5v-4.5Z"
						/>
					</svg>
					{$i18n.t('Add Shortcut')}
				</button>
			</div>
		{/if}
	</div>

	<!-- Add/Edit Modal -->
	{#if showAddModal}
		<AddShortcutModal
			onClose={handleModalClose}
			editingShortcut={editingShortcut}
			preselectedModelId={preselectedModelId}
		/>
	{/if}
{/if}

<style>
	.flow-shortcuts-container {
		width: 100%;
		margin-bottom: 1.5rem;
	}

	.shortcut-item {
		min-height: 170px;
	}

	/* Ensure smooth animations */
	:global(.shortcut-item) {
		transition: transform 0.2s ease, opacity 0.2s ease;
	}

	/* Grid improvements */
	:global(.flow-shortcuts-container .grid) {
		gap: 1rem;
	}

	@media (min-width: 768px) {
		.shortcut-item {
			min-height: 190px;
		}

		:global(.flow-shortcuts-container .grid) {
			gap: 1.25rem;
		}
	}

	@media (max-width: 640px) {
		.shortcut-item {
			min-height: 160px;
		}

		:global(.flow-shortcuts-container .grid) {
			gap: 0.875rem;
		}
	}
</style>
