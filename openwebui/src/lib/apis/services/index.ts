import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface ServiceStatus {
	authorized: boolean;
	email?: string;
	expires_at?: string;
	scopes?: string;
}

export interface ServicesStatusResponse {
	[service_id: string]: ServiceStatus;
}

export interface ConfiguredService {
	name: string;
	scopes: string[];
}

export interface ConfiguredServicesResponse {
	[service_id: string]: ConfiguredService;
}

export interface AuthResponse {
	auth_url: string;
	state: string;
}

export const getServicesStatus = async (token: string): Promise<ServicesStatusResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/services/status`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getConfiguredServices = async (): Promise<ConfiguredServicesResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/services/configured`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json'
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const initiateServiceAuth = async (
	token: string,
	serviceId: string
): Promise<AuthResponse> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/services/${serviceId}/auth`, {
		method: 'GET',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const disconnectService = async (
	token: string,
	serviceId: string
): Promise<{ message: string }> => {
	let error = null;

	const res = await fetch(`${WEBUI_API_BASE_URL}/services/${serviceId}/disconnect`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			error = err.detail;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const connectService = async (token: string, serviceId: string): Promise<void> => {
	const authResponse = await initiateServiceAuth(token, serviceId);

	if (!authResponse) {
		throw new Error('Failed to initiate OAuth flow');
	}

	// Open OAuth flow in popup window
	const width = 600;
	const height = 700;
	const left = window.screen.width / 2 - width / 2;
	const top = window.screen.height / 2 - height / 2;

	const popup = window.open(
		authResponse.auth_url,
		'oauth_popup',
		`width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`
	);

	// Wait for OAuth callback message
	return new Promise((resolve, reject) => {
		const messageHandler = (event: MessageEvent) => {
			if (event.data?.type === 'oauth_success' && event.data?.service_id === serviceId) {
				window.removeEventListener('message', messageHandler);
				resolve();
			} else if (event.data?.type === 'oauth_error') {
				window.removeEventListener('message', messageHandler);
				reject(new Error(event.data?.description || 'OAuth authorization failed'));
			}
		};

		window.addEventListener('message', messageHandler);

		// Cleanup if popup is closed without completing auth
		const checkClosed = setInterval(() => {
			if (popup && popup.closed) {
				clearInterval(checkClosed);
				window.removeEventListener('message', messageHandler);
				reject(new Error('OAuth popup was closed'));
			}
		}, 500);
	});
};
