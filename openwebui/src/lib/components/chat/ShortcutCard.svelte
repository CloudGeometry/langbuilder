<script lang="ts">
	import { getContext } from 'svelte';
	import { models } from '$lib/stores';

	const i18n = getContext('i18n');

	export let shortcut: {
		id: string;
		modelId: string;
		title: string;
		description?: string;
		icon: string;
		iconColor?: string;
		color?: string;
		prompt?: string;
		autoSubmit: boolean;
		enabled: boolean;
		order: number;
	};
	export let idx: number = 0;
	export let onClick: () => void = () => {};
	export let editMode: boolean = false;
	export let onEdit: () => void = () => {};
	export let onDelete: () => void = () => {};

	// Get model name for display
	$: modelName = shortcut.modelId
		? $models.find(m => m.id === shortcut.modelId)?.name || shortcut.modelId
		: 'No model';

	// Default icon color if not specified
	$: iconColor = shortcut.iconColor ?? shortcut.color ?? 'rgba(59, 130, 246, 0.15)';

	// Extract RGB values for gradient generation
	$: rgbValues = (() => {
		const rgbaMatch = iconColor.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
		if (rgbaMatch) {
			return {
				r: parseInt(rgbaMatch[1]),
				g: parseInt(rgbaMatch[2]),
				b: parseInt(rgbaMatch[3])
			};
		}
		return { r: 59, g: 130, b: 246 }; // Default blue
	})();
</script>

<button
	role="listitem"
	class="shortcut-card group"
	on:click={onClick}
	aria-label={shortcut.description || shortcut.title}
>
	<!-- Glassmorphism background with gradient -->
	<div class="card-background"></div>

	<!-- Gradient overlay based on icon color -->
	<div
		class="card-gradient"
		style="background: linear-gradient(135deg,
			rgba({rgbValues.r}, {rgbValues.g}, {rgbValues.b}, 0.1) 0%,
			rgba({rgbValues.r}, {rgbValues.g}, {rgbValues.b}, 0.05) 100%);"
	></div>

	<!-- Content -->
	<div class="card-content">
		<!-- Drag handle -->
		{#if editMode}
			<div class="drag-handle">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-4 h-4">
					<path d="M2 6.75A.75.75 0 0 1 2.75 6h10.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 6.75ZM2 9.25a.75.75 0 0 1 .75-.75h10.5a.75.75 0 0 1 0 1.5H2.75A.75.75 0 0 1 2 9.25Z" />
				</svg>
			</div>
		{/if}

		<!-- Edit/Delete buttons -->
		{#if editMode}
			<div class="action-buttons">
				<button
					class="action-btn edit-btn"
					on:click|stopPropagation={onEdit}
					aria-label="Edit"
				>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
						<path d="M13.488 2.513a1.75 1.75 0 0 0-2.475 0L6.75 6.774a2.75 2.75 0 0 0-.596.892l-.848 2.047a.75.75 0 0 0 .98.98l2.047-.848a2.75 2.75 0 0 0 .892-.596l4.261-4.262a1.75 1.75 0 0 0 0-2.474Z" />
						<path d="M4.75 3.5c-.69 0-1.25.56-1.25 1.25v6.5c0 .69.56 1.25 1.25 1.25h6.5c.69 0 1.25-.56 1.25-1.25V9A.75.75 0 0 1 14 9v2.25A2.75 2.75 0 0 1 11.25 14h-6.5A2.75 2.75 0 0 1 2 11.25v-6.5A2.75 2.75 0 0 1 4.75 2H7a.75.75 0 0 1 0 1.5H4.75Z" />
					</svg>
				</button>
				<button
					class="action-btn delete-btn"
					on:click|stopPropagation={onDelete}
					aria-label="Delete"
				>
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3.5 h-3.5">
						<path fill-rule="evenodd" d="M5 3.25V4H2.75a.75.75 0 0 0 0 1.5h.3l.815 8.15A1.5 1.5 0 0 0 5.357 15h5.285a1.5 1.5 0 0 0 1.493-1.35l.815-8.15h.3a.75.75 0 0 0 0-1.5H11v-.75A2.25 2.25 0 0 0 8.75 1h-1.5A2.25 2.25 0 0 0 5 3.25Zm2.25-.75a.75.75 0 0 0-.75.75V4h3v-.75a.75.75 0 0 0-.75-.75h-1.5ZM6.05 6a.75.75 0 0 1 .787.713l.275 5.5a.75.75 0 0 1-1.498.075l-.275-5.5A.75.75 0 0 1 6.05 6Zm3.9 0a.75.75 0 0 1 .712.787l-.275 5.5a.75.75 0 0 1-1.498-.075l.275-5.5a.75.75 0 0 1 .786-.711Z" clip-rule="evenodd" />
					</svg>
				</button>
			</div>
		{/if}

		<!-- Icon with animated background -->
		<div class="icon-container">
			<div
				class="icon-background"
				style="background: {iconColor};"
			></div>
			<div class="icon-emoji">
				{shortcut.icon}
			</div>
		</div>

		<!-- Text content -->
		<div class="text-content">
			<h3 class="card-title">{shortcut.title}</h3>
			{#if shortcut.description}
				<p class="card-description">{shortcut.description}</p>
			{/if}
		</div>

		<!-- Footer with badges -->
		<div class="card-footer">
			<!-- Model badge -->
			<div class="badge model-badge">
				<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3">
					<path d="M2 3a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3Z"/>
					<path fill-rule="evenodd" d="M13 6H3v6a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V6ZM5.72 7.47a.75.75 0 0 1 1.06 0L8 8.69l1.22-1.22a.75.75 0 1 1 1.06 1.06L9.06 9.75l1.22 1.22a.75.75 0 1 1-1.06 1.06L8 10.81l-1.22 1.22a.75.75 0 0 1-1.06-1.06l1.22-1.22-1.22-1.22a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd"/>
				</svg>
				<span class="truncate">{modelName}</span>
			</div>

			<!-- Prompt badge -->
			{#if shortcut.prompt}
				<div class="badge prompt-badge">
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" fill="currentColor" class="w-3 h-3">
						<path d="M2.87 2.298a.75.75 0 0 0-.812 1.021L3.39 6.624a1 1 0 0 0 .928.626H8.25a.75.75 0 0 1 0 1.5H4.318a1 1 0 0 0-.927.626l-1.333 3.305a.75.75 0 0 0 .811 1.022 24.89 24.89 0 0 0 11.236-5.423.75.75 0 0 0 0-1.06A24.89 24.89 0 0 0 2.869 2.298Z" />
					</svg>
					<span>Prompt</span>
				</div>
			{/if}
		</div>
	</div>

	<!-- Shine effect on hover -->
	<div class="shine-effect"></div>
</button>

<style>
	/* Card container */
	.shortcut-card {
		position: relative;
		min-height: 170px;
		width: 100%;
		border-radius: 16px;
		overflow: hidden;
		cursor: pointer;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		border: 1.5px solid transparent;
	}

	/* Glassmorphism background */
	.card-background {
		position: absolute;
		inset: 0;
		background: linear-gradient(145deg,
			rgba(255, 255, 255, 0.9) 0%,
			rgba(255, 255, 255, 0.7) 100%
		);
		backdrop-filter: blur(10px);
		-webkit-backdrop-filter: blur(10px);
		transition: all 0.3s ease;
	}

	:global(.dark) .card-background {
		background: linear-gradient(145deg,
			rgba(31, 41, 55, 0.8) 0%,
			rgba(17, 24, 39, 0.9) 100%
		);
	}

	/* Gradient overlay */
	.card-gradient {
		position: absolute;
		inset: 0;
		opacity: 0.6;
		transition: opacity 0.3s ease;
	}

	/* Shine effect */
	.shine-effect {
		position: absolute;
		top: -50%;
		left: -50%;
		width: 200%;
		height: 200%;
		background: linear-gradient(
			to bottom right,
			rgba(255, 255, 255, 0) 0%,
			rgba(255, 255, 255, 0.1) 50%,
			rgba(255, 255, 255, 0) 100%
		);
		transform: translateX(-100%) translateY(-100%) rotate(45deg);
		transition: transform 0.6s ease;
		pointer-events: none;
	}

	.shortcut-card:hover .shine-effect {
		transform: translateX(100%) translateY(100%) rotate(45deg);
	}

	/* Hover effects */
	.shortcut-card:hover {
		transform: translateY(-4px) scale(1.02);
		border-color: rgba(59, 130, 246, 0.3);
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.1),
			0 10px 10px -5px rgba(0, 0, 0, 0.04),
			0 0 0 1px rgba(59, 130, 246, 0.1);
	}

	:global(.dark) .shortcut-card:hover {
		border-color: rgba(96, 165, 250, 0.4);
		box-shadow:
			0 20px 25px -5px rgba(0, 0, 0, 0.3),
			0 10px 10px -5px rgba(0, 0, 0, 0.2),
			0 0 0 1px rgba(96, 165, 250, 0.2);
	}

	.shortcut-card:hover .card-background {
		background: linear-gradient(145deg,
			rgba(255, 255, 255, 0.95) 0%,
			rgba(255, 255, 255, 0.85) 100%
		);
	}

	:global(.dark) .shortcut-card:hover .card-background {
		background: linear-gradient(145deg,
			rgba(31, 41, 55, 0.9) 0%,
			rgba(17, 24, 39, 0.95) 100%
		);
	}

	.shortcut-card:hover .card-gradient {
		opacity: 0.8;
	}

	.shortcut-card:active {
		transform: translateY(-2px) scale(1.01);
	}

	/* Content container */
	.card-content {
		position: relative;
		display: flex;
		flex-direction: column;
		height: 100%;
		padding: 1rem;
		gap: 0.75rem;
		z-index: 1;
	}

	/* Drag handle */
	.drag-handle {
		position: absolute;
		top: 0.5rem;
		left: 50%;
		transform: translateX(-50%);
		color: rgba(107, 114, 128, 0.5);
		cursor: grab;
		transition: all 0.2s ease;
		z-index: 10;
	}

	.drag-handle:active {
		cursor: grabbing;
	}

	.drag-handle:hover {
		color: rgba(107, 114, 128, 0.8);
		transform: translateX(-50%) scale(1.1);
	}

	/* Action buttons */
	.action-buttons {
		position: absolute;
		top: 0.5rem;
		right: 0.5rem;
		display: flex;
		gap: 0.25rem;
		z-index: 10;
	}

	.action-btn {
		padding: 0.375rem;
		border-radius: 0.5rem;
		transition: all 0.2s ease;
		backdrop-filter: blur(8px);
		-webkit-backdrop-filter: blur(8px);
	}

	.edit-btn {
		background: rgba(59, 130, 246, 0.1);
		color: rgb(37, 99, 235);
	}

	.edit-btn:hover {
		background: rgba(59, 130, 246, 0.2);
		transform: scale(1.1);
	}

	:global(.dark) .edit-btn {
		color: rgb(96, 165, 250);
	}

	.delete-btn {
		background: rgba(239, 68, 68, 0.1);
		color: rgb(220, 38, 38);
	}

	.delete-btn:hover {
		background: rgba(239, 68, 68, 0.2);
		transform: scale(1.1);
	}

	:global(.dark) .delete-btn {
		color: rgb(248, 113, 113);
	}

	/* Icon container */
	.icon-container {
		position: relative;
		width: 64px;
		height: 64px;
		margin: 0 auto;
		flex-shrink: 0;
	}

	.icon-background {
		position: absolute;
		inset: 0;
		border-radius: 16px;
		opacity: 1;
		transition: all 0.3s ease;
		filter: blur(0px);
	}

	.shortcut-card:hover .icon-background {
		filter: blur(2px);
		transform: scale(1.1);
		opacity: 0.9;
	}

	.icon-emoji {
		position: relative;
		width: 100%;
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 2rem;
		transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
		z-index: 1;
	}

	.shortcut-card:hover .icon-emoji {
		transform: scale(1.15) rotate(5deg);
	}

	/* Text content */
	.text-content {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		min-height: 0;
	}

	.card-title {
		font-size: 0.875rem;
		font-weight: 600;
		color: rgb(17, 24, 39);
		line-height: 1.25;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
		transition: color 0.2s ease;
	}

	:global(.dark) .card-title {
		color: rgb(243, 244, 246);
	}

	.shortcut-card:hover .card-title {
		color: rgb(37, 99, 235);
	}

	:global(.dark) .shortcut-card:hover .card-title {
		color: rgb(96, 165, 250);
	}

	.card-description {
		font-size: 0.75rem;
		color: rgb(107, 114, 128);
		line-height: 1.3;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	:global(.dark) .card-description {
		color: rgb(156, 163, 175);
	}

	/* Footer badges */
	.card-footer {
		display: flex;
		flex-wrap: wrap;
		gap: 0.375rem;
		margin-top: auto;
		padding-top: 0.5rem;
		border-top: 1px solid rgba(229, 231, 235, 0.8);
	}

	:global(.dark) .card-footer {
		border-top-color: rgba(75, 85, 99, 0.5);
	}

	.badge {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.25rem 0.5rem;
		border-radius: 0.375rem;
		font-size: 0.6875rem;
		font-weight: 500;
		transition: all 0.2s ease;
		max-width: 100%;
	}

	.model-badge {
		background: rgba(59, 130, 246, 0.1);
		color: rgb(37, 99, 235);
		border: 1px solid rgba(59, 130, 246, 0.2);
	}

	:global(.dark) .model-badge {
		background: rgba(59, 130, 246, 0.15);
		color: rgb(147, 197, 253);
		border-color: rgba(59, 130, 246, 0.3);
	}

	.prompt-badge {
		background: rgba(16, 185, 129, 0.1);
		color: rgb(5, 150, 105);
		border: 1px solid rgba(16, 185, 129, 0.2);
	}

	:global(.dark) .prompt-badge {
		background: rgba(16, 185, 129, 0.15);
		color: rgb(110, 231, 183);
		border-color: rgba(16, 185, 129, 0.3);
	}

	.shortcut-card:hover .badge {
		transform: translateY(-1px);
	}

	/* Responsive adjustments */
	@media (min-width: 768px) {
		.shortcut-card {
			min-height: 190px;
		}

		.icon-container {
			width: 72px;
			height: 72px;
		}

		.icon-emoji {
			font-size: 2.25rem;
		}

		.card-title {
			font-size: 0.9375rem;
		}

		.card-description {
			font-size: 0.8125rem;
		}
	}

	@media (max-width: 640px) {
		.shortcut-card {
			min-height: 160px;
		}

		.icon-container {
			width: 56px;
			height: 56px;
		}

		.icon-emoji {
			font-size: 1.75rem;
		}

		.card-content {
			padding: 0.875rem;
			gap: 0.625rem;
		}
	}
</style>
