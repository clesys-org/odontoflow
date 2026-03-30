export interface ServiceItem {
  name: string;
  description: string;
  icon: string;
}

export interface ClinicWebsite {
  id: string;
  clinic_name: string;
  slug: string;
  tagline: string | null;
  description: string | null;
  phone: string | null;
  whatsapp: string | null;
  email: string | null;
  address: string | null;
  primary_color: string;
  services: ServiceItem[];
  working_hours_text: string | null;
  social_links: Record<string, string>;
  seo_title: string | null;
  seo_description: string | null;
  booking_enabled: boolean;
  published: boolean;
}
