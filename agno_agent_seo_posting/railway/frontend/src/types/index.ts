// Type definitions for WordPress SEO Publishing System

// Image configuration types
export interface ImageConfigs {
  resize_method: 'fixed_width' | 'google_docs_original' | 'no_resize';
  target_width: number;
  target_height: number | null;
  image_quality: number;
  image_format: 'JPEG' | 'PNG' | 'WEBP';
  enable_auto_captions: boolean;
  naming_method: 'default' | 'alt_text' | 'main_keyword';
  alt_text_words?: number;
}

// HTML transformation pattern
export interface HtmlPattern {
  element_type: string;
  source_pattern: string;
  target_pattern: string;
}

// HTML configuration types
export interface HtmlConfigs {
  patterns: HtmlPattern[];
}

// Project type
export interface Project {
  projectId: string;
  projectName: string;
  wordpressUrl: string;
  wordpressUsername: string;
  wordpressAppPassword: string;
  htmlConfigs: HtmlConfigs | null;
  imageConfigs: ImageConfigs | null;
  status: string;
  notes: string | null;
  createdAt: Date;
  updatedAt: Date;
  lastPublishedAt: Date | null;
}

// Publishing history type
export interface PublishingHistory {
  id: number;
  projectId: string | null;
  googleDocsUrl: string;
  wordpressPostId: number | null;
  wordpressPostUrl: string | null;
  postTitle: string | null;
  postStatus: string | null;
  imagesProcessed: number;
  success: boolean;
  errorMessage: string | null;
  executionTimeSeconds: number | null;
  publishedAt: Date;
  project?: Project | null;
}

// API response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Publishing workflow result
export interface PublishingResult {
  success: boolean;
  post_url?: string;
  edit_url?: string;
  post_id?: number;
  post_title?: string;
  post_status?: string;
  images_processed?: number;
  execution_time?: number;
  google_drive_folder_url?: string;
  google_drive_folder_name?: string;
  error?: string;
  step_failed?: string;
}

// Form types for creating/editing projects
export interface ProjectFormData {
  projectId: string;
  projectName: string;
  wordpressUrl: string;
  wordpressUsername: string;
  wordpressAppPassword: string;
  imageConfigs: ImageConfigs;
  notes?: string;
}

// Pattern modification request
export interface PatternModifyRequest {
  current_patterns: HtmlPattern[];
  instruction: string;
}

// Pattern modification result
export interface PatternModifyResult {
  success: boolean;
  patterns?: HtmlPattern[];
  changes_made?: string;
  error?: string;
}

// HTML scan result
export interface HtmlScanResult {
  success: boolean;
  patterns?: HtmlPattern[];
  error?: string;
}
