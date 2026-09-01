export const formatTHB = (amount: number | string) =>
    new Intl.NumberFormat('th-TH', {
        style: 'currency',
        currency: 'THB',
        maximumFractionDigits: 0,
    }).format(Number(amount));
