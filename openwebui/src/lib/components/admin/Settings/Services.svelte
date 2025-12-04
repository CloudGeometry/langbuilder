<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	const i18n = getContext('i18n');

	import {
		getServicesStatus,
		getConfiguredServices,
		connectService,
		disconnectService,
		type ServicesStatusResponse,
		type ConfiguredServicesResponse
	} from '$lib/apis/services';

	import Switch from '$lib/components/common/Switch.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';

	let loading = true;
	let servicesStatus: ServicesStatusResponse = {};
	let configuredServices: ConfiguredServicesResponse = {};
	let connecting: { [key: string]: boolean } = {};

	const serviceIcons: { [key: string]: string } = {
		google_drive:
			'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 87.3 78" class="size-5"><path fill="#0066da" d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z"/><path fill="#00ac47" d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0-1.2 4.5h27.5z"/><path fill="#ea4335" d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z"/><path fill="#00832d" d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z"/><path fill="#2684fc" d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z"/><path fill="#ffba00" d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 28h27.45c0-1.55-.4-3.1-1.2-4.5z"/></svg>',
		zoho: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-5"><path fill="currentColor" d="M3.75 3C2.78 3 2 3.78 2 4.75v14.5c0 .97.78 1.75 1.75 1.75h16.5c.97 0 1.75-.78 1.75-1.75V4.75C22 3.78 21.22 3 20.25 3zm0 1.5h16.5a.25.25 0 0 1 .25.25v14.5a.25.25 0 0 1-.25.25H3.75a.25.25 0 0 1-.25-.25V4.75a.25.25 0 0 1 .25-.25zM6 7v1.5h9.793L6 18.293V20h12v-1.5H8.207L18 8.707V7z"/></svg>',
		jira: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-5"><path fill="#2684ff" d="M11.53 2c0 2.4 1.97 4.35 4.35 4.35h1.78v1.7c0 2.4 1.94 4.35 4.34 4.35V2.84a.84.84 0 0 0-.84-.84zM6.77 6.8a4.36 4.36 0 0 0 4.35 4.35h1.78v1.7a4.36 4.36 0 0 0 4.35 4.35V7.63a.83.83 0 0 0-.84-.83zM2 11.6c0 2.4 1.95 4.35 4.35 4.35h1.78v1.7c0 2.4 1.95 4.35 4.35 4.35v-9.57a.84.84 0 0 0-.84-.84z"/></svg>',
		hubspot:
			'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="size-5"><path fill="#ff7a59" d="M18.164 7.93V5.084a2.198 2.198 0 0 0 .522-1.418c0-1.226-.995-2.22-2.222-2.22-1.226 0-2.22.994-2.22 2.22 0 .574.217 1.096.573 1.495v2.77a4.593 4.593 0 0 0-2.023 1.42L7.6 6.11a2.81 2.81 0 0 0 .209-.928c0-1.228-.892-2.22-2.12-2.22-1.228 0-2.22.992-2.22 2.22 0 1.098.797 2.01 1.848 2.183l.017.005 5.356 3.874a4.476 4.476 0 0 0-.354 1.735 4.55 4.55 0 0 0 4.546 4.546 4.55 4.55 0 0 0 4.545-4.546 4.543 4.543 0 0 0-2.703-4.15l-.559.946-.001-.001zM14.738 19.41a.99.99 0 0 0 .716-.306l2.429-2.43a.998.998 0 1 0-1.414-1.414l-2.43 2.429a.998.998 0 0 0 .699 1.721z"/></svg>'
	};

	const serviceDisplayNames: { [key: string]: string } = {
		google_drive: 'Google Drive',
		zoho: 'Zoho People',
		jira: 'JIRA',
		hubspot: 'HubSpot'
	};

	const loadServices = async () => {
		loading = true;
		try {
			const [status, configured] = await Promise.all([
				getServicesStatus(localStorage.token),
				getConfiguredServices()
			]);

			servicesStatus = status;
			configuredServices = configured;
		} catch (error) {
			console.error('Failed to load services:', error);
			toast.error($i18n.t('Failed to load services'));
		} finally {
			loading = false;
		}
	};

	const handleConnect = async (serviceId: string) => {
		connecting[serviceId] = true;
		try {
			await connectService(localStorage.token, serviceId);
			toast.success($i18n.t('Successfully connected to {{service}}', { service: serviceDisplayNames[serviceId] }));
			await loadServices();
		} catch (error) {
			console.error('Failed to connect:', error);
			toast.error(error instanceof Error ? error.message : $i18n.t('Failed to connect to service'));
		} finally {
			connecting[serviceId] = false;
		}
	};

	const handleDisconnect = async (serviceId: string) => {
		connecting[serviceId] = true;
		try {
			await disconnectService(localStorage.token, serviceId);
			toast.success($i18n.t('Successfully disconnected from {{service}}', { service: serviceDisplayNames[serviceId] }));
			await loadServices();
		} catch (error) {
			console.error('Failed to disconnect:', error);
			toast.error($i18n.t('Failed to disconnect from service'));
		} finally {
			connecting[serviceId] = false;
		}
	};

	onMount(async () => {
		await loadServices();
	});
</script>

<div class="flex flex-col h-full justify-between text-sm">
	<div class="overflow-y-scroll scrollbar-hidden h-full">
		{#if loading}
			<div class="flex h-full justify-center">
				<div class="my-auto">
					<Spinner className="size-6" />
				</div>
			</div>
		{:else}
			<div class="">
				<div class="mb-3">
					<div class="mt-0.5 mb-2.5 text-base font-medium">{$i18n.t('Service Integrations')}</div>

					<hr class="border-gray-100 dark:border-gray-850 my-2" />

					<div class="text-xs text-gray-500 mb-3">
						{$i18n.t('Connect external services to enable enhanced functionality')}
					</div>

					<div class="flex flex-col gap-2">
						{#each Object.entries(configuredServices) as [serviceId, service]}
							{@const status = servicesStatus[serviceId]}
							{@const isConnected = status?.authorized ?? false}

							<div
								class="flex items-center justify-between p-3 rounded-lg border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition"
							>
								<div class="flex items-center gap-3">
									<div class="shrink-0">
										{#if serviceIcons[serviceId]}
											{@html serviceIcons[serviceId]}
										{:else}
											<div class="size-5 bg-gray-300 dark:bg-gray-600 rounded" />
										{/if}
									</div>

									<div class="flex flex-col">
										<div class="font-medium">{serviceDisplayNames[serviceId] || service.name}</div>
										{#if isConnected && status?.email}
											<div class="text-xs text-gray-500">{status.email}</div>
										{:else}
											<div class="text-xs text-gray-500">
												{$i18n.t('Not connected')}
											</div>
										{/if}
									</div>
								</div>

								<div class="flex items-center gap-2">
									{#if connecting[serviceId]}
										<Spinner className="size-4" />
									{/if}

									<Switch
										state={isConnected}
										on:change={async (e) => {
											const newState = e.detail;
											if (newState) {
												await handleConnect(serviceId);
											} else {
												await handleDisconnect(serviceId);
											}
										}}
										disabled={connecting[serviceId]}
									/>
								</div>
							</div>
						{/each}

						{#if Object.keys(configuredServices).length === 0}
							<div class="text-center py-8 text-gray-500">
								{$i18n.t('No services are configured. Contact your administrator to set up service integrations.')}
							</div>
						{/if}
					</div>

					{#if Object.keys(configuredServices).length > 0}
						<div class="mt-4 text-xs text-gray-500">
							<div class="font-medium mb-1">{$i18n.t('Available Services:')}</div>
							<ul class="list-disc list-inside space-y-0.5">
								<li>
									<strong>Google Drive:</strong>
									{$i18n.t('Search and access files from Google Drive')}
								</li>
								<li>
									<strong>Zoho People:</strong>
									{$i18n.t('Access employee profiles, attendance, and leave data')}
								</li>
								<li>
									<strong>JIRA:</strong>
									{$i18n.t('Manage and search JIRA issues')}
								</li>
							</ul>
						</div>
					{/if}
				</div>
			</div>
		{/if}
	</div>
</div>
