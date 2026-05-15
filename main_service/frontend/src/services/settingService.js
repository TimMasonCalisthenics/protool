import { getAuthHeaders, API_BASE_URL } from '@services/interceptor';
const API_BASE_URL_PRODUCTS = API_BASE_URL + 'system';


export const getActiveProduct = async () => {

    const response = await fetch(API_BASE_URL_PRODUCTS + '/active_product', {
        method: 'GET',
        headers: getAuthHeaders(),
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.message || 'Failed to active product');
    }
    return result;

}

export const setActiveProduct = async (productId) => {
    const response = await fetch(API_BASE_URL_PRODUCTS + '/active_product', {
        method: 'PATCH',
        headers: {
            ...getAuthHeaders(),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ product_id: productId }),
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.message || 'Failed to set active product');
    }
    return result;

}

export const getActiveProductDetail = async () => {
    const response = await fetch(API_BASE_URL_PRODUCTS + '/active_product_detail', {
        method: 'GET',
        headers: getAuthHeaders(),
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.message || 'Failed to get active product detail');
    }
    return result;
}
