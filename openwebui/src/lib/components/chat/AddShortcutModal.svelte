<script lang="ts">
	/**
	 * AddShortcutModal Component
	 *
	 * Modal for creating and editing model shortcuts.
	 *
	 * @prop {Function} onClose - Callback when modal closes
	 * @prop {Object|null} editingShortcut - Shortcut being edited (null for create mode)
	 * @prop {string|null} preselectedModelId - Model ID to pre-select (for quick add)
	 */

	import { onMount, getContext } from 'svelte';
	import { settings, user, models as modelsStore } from '$lib/stores';
	import { getUserSettings, updateUserSettings } from '$lib/apis/users';
	import { toast } from 'svelte-sonner';

	const i18n = getContext('i18n');

	export let onClose: () => void;
	export let editingShortcut: any = null;
	export let preselectedModelId: string | null = null;

	// Form state
	let formData = {
		modelId: '',
		title: '',
		description: '',
		icon: '⚡',
		iconColor: 'rgba(59, 130, 246, 0.15)',
		prompt: '',
		autoSubmit: false,
		enabled: true,
		order: 0
	};

	// Color picker helper
	let hexColor = '#3b82f6'; // Default blue

	// UI state
	let saving = false;
	let errorMessage = '';

	// Validation state
	let validationErrors = {
		modelId: false,
		title: false
	};

	// Convert hex to rgba
	$: {
		if (hexColor) {
			const r = parseInt(hexColor.slice(1, 3), 16);
			const g = parseInt(hexColor.slice(3, 5), 16);
			const b = parseInt(hexColor.slice(5, 7), 16);
			formData.iconColor = `rgba(${r}, ${g}, ${b}, 0.15)`;
		}
	}

	// CREATE MODE with preselected model (from "Add" button)
	$: if (preselectedModelId && !editingShortcut && !formData.modelId) {
		console.log('🎯 [AddShortcutModal] Handling preselection for:', preselectedModelId);

		formData.modelId = preselectedModelId;

		// Auto-generate title from model name
		const selectedModel = $modelsStore.find(m => m.id === preselectedModelId);
		if (selectedModel) {
			formData.title = selectedModel.name.substring(0, 30); // Respect max length
		}

		console.log('📝 [AddShortcutModal] Auto-populated:', { modelId: formData.modelId, title: formData.title });
	}

	// Pre-populate form when editing
	onMount(() => {
		if (editingShortcut) {
			formData = {
				modelId: editingShortcut.modelId || '',
				title: editingShortcut.title || '',
				description: editingShortcut.description || '',
				icon: editingShortcut.icon || '⚡',
				iconColor: editingShortcut.iconColor || 'rgba(59, 130, 246, 0.15)',
				prompt: editingShortcut.prompt || '',
				autoSubmit: editingShortcut.autoSubmit || false,
				enabled: editingShortcut.enabled !== false,
				order: editingShortcut.order || 0
			};

			// Extract hex from rgba for color picker
			const rgbaMatch = formData.iconColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
			if (rgbaMatch) {
				const r = parseInt(rgbaMatch[1]).toString(16).padStart(2, '0');
				const g = parseInt(rgbaMatch[2]).toString(16).padStart(2, '0');
				const b = parseInt(rgbaMatch[3]).toString(16).padStart(2, '0');
				hexColor = `#${r}${g}${b}`;
			}
		}
	});

	// Validation function
	const validateForm = (): boolean => {
		// Reset validation errors
		validationErrors = {
			modelId: !formData.modelId,
			title: !formData.title
		};

		return !!formData.modelId && !!formData.title;
	};

	// Reset form
	const resetForm = () => {
		formData = {
			modelId: '',
			title: '',
			description: '',
			icon: '⚡',
			iconColor: 'rgba(59, 130, 246, 0.15)',
			prompt: '',
			autoSubmit: false,
			enabled: true,
			order: 0
		};
		hexColor = '#3b82f6';
		errorMessage = '';
	};

	// Form submission handler
	const handleSubmit = async () => {
		console.log('📝 [AddShortcutModal] handleSubmit started');
		errorMessage = '';

		// Validate
		if (!validateForm()) {
			errorMessage = 'Please fill in all required fields';
			console.error('❌ [AddShortcutModal] Validation failed:', { formData });
			return;
		}

		try {
			saving = true;

			// Validate token exists
			if (!localStorage.token) {
				throw new Error('Authentication token not found. Please log in again.');
			}

			// Fetch current settings from API using the proper function
			console.log('🔍 [AddShortcutModal] Fetching current settings from API...');

			let freshSettings;
			try {
				freshSettings = await getUserSettings(localStorage.token);
			} catch (apiError) {
				console.error('❌ [AddShortcutModal] Failed to get user settings:', apiError);
				throw new Error('Failed to load settings. Please try again.');
			}

			// Validate freshSettings structure
			if (!freshSettings || typeof freshSettings !== 'object') {
				console.error('❌ [AddShortcutModal] Invalid settings structure:', freshSettings);
				throw new Error('Invalid settings data received. Please try again.');
			}

			// Get current shortcuts with fallback
			const currentShortcuts = freshSettings?.ui?.flowShortcuts?.shortcuts ?? [];

			// Validate currentShortcuts is an array
			if (!Array.isArray(currentShortcuts)) {
				console.error('❌ [AddShortcutModal] shortcuts is not an array:', currentShortcuts);
				throw new Error('Invalid shortcuts data structure. Please contact support.');
			}

			let updatedShortcuts;

			// Update vs. create logic
			if (editingShortcut) {
				// Update existing shortcut - preserve createdAt, update updatedAt
				updatedShortcuts = currentShortcuts.map((s) =>
					s.id === editingShortcut.id
						? {
							...formData,
							id: editingShortcut.id,
							createdAt: editingShortcut.createdAt || Date.now(),
							updatedAt: Date.now()
						}
						: s
				);
				console.log('✏️ Updating shortcut:', editingShortcut.id);
			} else {
				// Generate unique ID for new shortcut with timestamps
				const now = Date.now();
				const newShortcut = {
					...formData,
					id: crypto.randomUUID(),
					createdAt: now,
					updatedAt: now
				};
				console.log('➕ Creating shortcut:', newShortcut);

				// Add to shortcuts array
				updatedShortcuts = [...currentShortcuts, newShortcut];
			}

			// Save to database
			const updatedSettings = {
				...freshSettings,
				ui: {
					...freshSettings.ui,
					flowShortcuts: {
						...freshSettings.ui?.flowShortcuts,
						shortcuts: updatedShortcuts
					}
				}
			};

			console.log('💾 [AddShortcutModal] Preparing to save:', {
				shortcutsCount: updatedShortcuts.length,
				operation: editingShortcut ? 'update' : 'create'
			});

			// Validate updatedSettings before saving
			if (!updatedSettings.ui?.flowShortcuts || !Array.isArray(updatedSettings.ui.flowShortcuts.shortcuts)) {
				console.error('❌ [AddShortcutModal] Invalid updatedSettings structure:', updatedSettings);
				throw new Error('Failed to prepare settings for save. Please try again.');
			}

			// Save to API
			let response;
			try {
				response = await updateUserSettings(localStorage.token, updatedSettings);
			} catch (saveError) {
				console.error('❌ [AddShortcutModal] Save error:', saveError);
				throw new Error('Failed to save to server: ' + (saveError?.message || 'Unknown error'));
			}

			// Validate save response
			if (!response) {
				console.error('❌ [AddShortcutModal] No response from updateUserSettings');
				throw new Error('No response from server. Changes may not have been saved.');
			}

			console.log('✅ [AddShortcutModal] Save successful:', response);

			// Handle success - Update local store
			try {
				settings.set(updatedSettings);
			} catch (storeError) {
				console.error('⚠️ [AddShortcutModal] Failed to update store:', storeError);
				// Don't throw - data is saved to server, store update is optional
			}

			toast.success(
				editingShortcut
					? 'Shortcut updated successfully'
					: `Shortcut created for ${formData.title}`
			);

			// Reset form
			resetForm();

			// Close modal (reactivity handles display refresh)
			onClose();
		} catch (error) {
			// Handle error
			console.error('❌ [AddShortcutModal] Fatal error:', {
				error,
				message: error?.message,
				stack: error?.stack
			});

			// Set user-friendly error message
			errorMessage = error?.message ?? 'Failed to save shortcut. Please try again.';

			// Show toast with error
			toast.error(errorMessage);
		} finally {
			saving = false;
			console.log('🏁 [AddShortcutModal] handleSubmit completed');
		}
	};

	// ESC key to close
	const handleKeydown = (e: KeyboardEvent) => {
		if (e.key === 'Escape') {
			onClose();
		}
	};

	onMount(() => {
		window.addEventListener('keydown', handleKeydown);
		return () => {
			window.removeEventListener('keydown', handleKeydown);
		};
	});

	// Click-outside to close
	const handleBackdropClick = (e: MouseEvent) => {
		if (e.target === e.currentTarget) {
			onClose();
		}
	};

	// Get display name for selected model
	$: selectedModelDisplay = formData.modelId
		? $modelsStore.find(m => m.id === formData.modelId)?.name || formData.modelId
		: 'No model selected';
</script>

<!-- Backdrop -->
<div
	class="fixed inset-0 bg-transparent z-50 flex items-center justify-center p-4"
	on:click={handleBackdropClick}
	on:keydown={handleKeydown}
	role="dialog"
	aria-modal="true"
	tabindex="-1"
>
	<!-- Modal Container -->
	<div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
		<div class="p-6">
			<!-- Header with Close Button -->
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
				{editingShortcut ? $i18n.t('Edit Shortcut') : $i18n.t('Add Shortcut')}
			</h2>
				<button
					on:click={onClose}
					class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
					aria-label="Close modal"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 20 20"
						fill="currentColor"
						class="w-5 h-5"
					>
						<path
							d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z"
						/>
					</svg>
				</button>
			</div>

			<!-- Form -->
			<form on:submit|preventDefault={handleSubmit} class="space-y-4">
				<!-- Model Selection Field -->
				<div>
					<label for="modelId" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n.t('Select Model')} *
					</label>

					<!-- Dropdown with real models from API -->
					<select
						id="modelId"
						bind:value={formData.modelId}
						required
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
						class:border-gray-300={!validationErrors.modelId}
						class:dark:border-gray-600={!validationErrors.modelId}
						class:border-red-500={validationErrors.modelId}
						class:dark:border-red-500={validationErrors.modelId}
					>
						<!-- Placeholder option -->
						<option value="" disabled>
							{$i18n.t('Select a model...')}
						</option>

						<!-- Populate with real models from API -->
						{#each $modelsStore as model (model.id)}
							<option value={model.id}>
								{model.name}
							</option>
						{/each}
					</select>

					<!-- Validation error message -->
					{#if validationErrors.modelId}
						<p class="text-xs text-red-600 dark:text-red-400 mt-1">
							{$i18n.t('Please select a model')}
						</p>
					{/if}

					<!-- Model count -->
					<p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
						{$modelsStore.length} {$i18n.t('model')}{$modelsStore.length !== 1 ? 's' : ''} {$i18n.t('available')}
					</p>
				</div>

				<!-- Title Field -->
				<div>
					<label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n.t('Shortcut Title')} *
					</label>
					<input
						id="title"
						type="text"
						bind:value={formData.title}
						placeholder={$i18n.t('e.g., GPT-4 Analysis')}
						maxlength="30"
						required
						class="w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
						class:border-gray-300={!validationErrors.title}
						class:dark:border-gray-600={!validationErrors.title}
						class:border-red-500={validationErrors.title}
						class:dark:border-red-500={validationErrors.title}
					/>
					<div class="flex justify-between items-center mt-1">
						<span class="text-xs text-gray-500 dark:text-gray-400">
							{formData.title.length}/30
						</span>
						{#if validationErrors.title}
							<p class="text-xs text-red-600 dark:text-red-400">
								{$i18n.t('Please enter a title')}
							</p>
						{/if}
					</div>
				</div>

				<!-- Description Field -->
				<div>
					<label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n.t('Description')} ({$i18n.t('optional')})
					</label>
					<textarea
						id="description"
						bind:value={formData.description}
						placeholder={$i18n.t('e.g., Use GPT-4 for complex analysis tasks')}
						maxlength="100"
						rows="2"
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
					></textarea>
					<span class="text-xs text-gray-500 dark:text-gray-400">
						{formData.description.length}/100
					</span>
				</div>

				<!-- Icon Picker -->
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n.t('Icon')}
					</label>
					<div class="flex gap-3 items-center">
						<div class="text-4xl">
							{formData.icon}
						</div>
						<input
							type="text"
							bind:value={formData.icon}
							placeholder={$i18n.t('Paste emoji...')}
							class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
						/>
					</div>
					<div class="flex gap-2 mt-2 flex-wrap">
						{#each ['🤖', '🧠', '💡', '🚀', '⚡', '✨', '🎯', '💬', '📊', '🔮'] as preset}
							<button
								type="button"
								on:click={() => formData.icon = preset}
								class="px-3 py-1 text-xl hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
							>
								{preset}
							</button>
						{/each}
					</div>
				</div>

				<!-- Color Picker -->
				<div>
					<label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n.t('Background Color')}
					</label>
					<div class="flex gap-3 items-center">
						<div
							class="w-12 h-12 rounded-lg border-2 border-gray-300 dark:border-gray-600"
							style="background: {formData.iconColor}"
						></div>
						<input
							type="color"
							bind:value={hexColor}
							class="w-16 h-10 cursor-pointer rounded border border-gray-300 dark:border-gray-600"
						/>
						<span class="text-sm text-gray-600 dark:text-gray-400 font-mono">
							{formData.iconColor}
						</span>
					</div>
					<div class="flex gap-2 mt-2">
						{#each [
							{name: 'Blue', hex: '#3b82f6'},
							{name: 'Green', hex: '#22c55e'},
							{name: 'Purple', hex: '#a855f7'},
							{name: 'Red', hex: '#ef4444'},
							{name: 'Orange', hex: '#f97316'}
						] as preset}
							<button
								type="button"
								on:click={() => hexColor = preset.hex}
								class="px-3 py-1 text-xs rounded border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
							>
								{preset.name}
							</button>
						{/each}
					</div>
				</div>

				<!-- Prompt Field -->
				<div>
					<label for="prompt" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
						{$i18n.t('Pre-fill Prompt')} ({$i18n.t('optional')})
					</label>
					<textarea
						id="prompt"
						bind:value={formData.prompt}
						placeholder={$i18n.t('Optional message to pre-fill in chat')}
						rows="3"
						class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
					></textarea>
				</div>

				<!-- Auto-submit Checkbox -->
				<div class="flex items-start gap-2">
					<input
						type="checkbox"
						id="autoSubmit"
						bind:checked={formData.autoSubmit}
						disabled={!formData.prompt}
						class="mt-1 w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
					/>
					<div class="flex-1">
						<label for="autoSubmit" class="text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer">
							{$i18n.t('Auto-submit prompt')}
						</label>
						{#if formData.autoSubmit}
							<span class="block text-xs text-orange-600 dark:text-orange-400 mt-1">
								⚠️ {$i18n.t('Prompt will be sent automatically')}
							</span>
						{/if}
					</div>
				</div>

				<!-- Error Message -->
				{#if errorMessage}
					<div class="mt-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
						<p class="text-sm text-red-600 dark:text-red-400">{errorMessage}</p>
					</div>
				{/if}

				<!-- Form Actions -->
				<div class="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
					<button
						type="button"
						on:click={onClose}
						disabled={saving}
						class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
					>
						{$i18n.t('Cancel')}
					</button>
					<button
						type="submit"
						disabled={saving}
						class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
					>
						{#if saving}
							<svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
								<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
								<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
							</svg>
							{editingShortcut ? $i18n.t('Updating...') : $i18n.t('Saving...')}
						{:else}
							{editingShortcut ? $i18n.t('Update Shortcut') : $i18n.t('Save Shortcut')}
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
</div>
