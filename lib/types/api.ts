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
