export type ApiFieldErrors = Record<string, string[]>;

export interface ApiErrorResponse {
  code: string;
  detail: string;
  fields: ApiFieldErrors;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Category {
  name: string;
  slug: string;
  description: string;
  display_order: number;
}

export interface ProductImage {
  url: string;
  alt_text: string;
  display_order: number;
}

export type ProductType = "coffee" | "equipment" | "drinkware";
export type Grind = "whole_bean" | "espresso" | "filter" | "";

export interface ProductVariant {
  sku: string;
  option_name: string;
  weight_grams: number | null;
  grind: Grind;
  price: string;
  available: boolean;
  available_quantity: number;
}

export interface ProductSummary {
  name: string;
  slug: string;
  product_type: ProductType;
  description: string;
  profile: string;
  is_featured: boolean;
  category: Category;
  starting_price: string;
  available: boolean;
  primary_image: ProductImage | null;
}

export interface ProductDetail extends ProductSummary {
  seo_title: string;
  seo_description: string;
  variants: ProductVariant[];
  images: ProductImage[];
}

export interface ProductFilters {
  category?: string;
  type?: ProductType;
  featured?: boolean;
  availability?: boolean;
  search?: string;
  minimum_price?: string;
  maximum_price?: string;
  ordering?: "name" | "-name" | "price" | "-price";
  page?: number;
  page_size?: number;
}

export type InquiryType = "hospitality" | "office" | "event" | "wholesale" | "other";

export interface PartnershipInquiryInput {
  name: string;
  email: string;
  phone: string;
  company: string;
  inquiry_type: InquiryType;
  requirements: string;
  consent: boolean;
  website: string;
}

export interface NewsletterSubscriptionInput {
  email: string;
  consent: boolean;
  consent_source: "storefront_footer";
  website: string;
}

export interface SubmissionResponse {
  detail: string;
}

export interface CartItem {
  public_id: string;
  variant_sku: string;
  product_name: string;
  option_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

export interface Cart {
  public_id: string;
  currency: "THB";
  items: CartItem[];
  subtotal: string;
  discount_total: string;
  shipping_total: string;
  tax_total: string;
  total: string;
  expires_at: string;
}

export interface ShippingAddress {
  full_name: string;
  phone: string;
  address_line_1: string;
  address_line_2: string;
  subdistrict: string;
  district: string;
  province: string;
  postal_code: string;
  country_code: "TH";
}

export interface ShippingMethod {
  code: "standard_th";
  name: string;
  fee: string;
  minimum_business_days: number;
  maximum_business_days: number;
}

export interface CheckoutPreviewInput {
  shipping_address: ShippingAddress;
  shipping_method: "standard_th";
}

export interface CheckoutPreview {
  cart: Cart;
  shipping_address: ShippingAddress;
  shipping_method: ShippingMethod;
}

export interface OrderCreateInput extends CheckoutPreviewInput {
  customer_email: string;
}

export type OrderStatus =
  | "awaiting_payment"
  | "confirmed"
  | "fulfilling"
  | "shipped"
  | "delivered"
  | "cancelled";

export interface OrderItem {
  product_name: string;
  sku: string;
  option_name: string;
  weight_grams: number | null;
  grind: Grind;
  unit_price: string;
  quantity: number;
  line_subtotal: string;
  discount_total: string;
  tax_total: string;
  line_total: string;
}

export interface Order {
  public_id: string;
  status: OrderStatus;
  customer_email: string;
  currency: "THB";
  shipping_method: "standard_th";
  shipping_method_name: string;
  shipping_address: ShippingAddress;
  items: OrderItem[];
  subtotal: string;
  discount_total: string;
  shipping_total: string;
  tax_total: string;
  total: string;
  created_at: string;
  updated_at: string;
}

export interface OrderStatusResponse {
  public_id: string;
  status: OrderStatus;
  currency: "THB";
  total: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentCheckoutSession {
  public_id: string;
  status: "creating" | "open" | "paid" | "failed" | "expired" | "refunded";
  checkout_url: string;
  amount: string;
  currency: "THB";
  expires_at: string;
}
