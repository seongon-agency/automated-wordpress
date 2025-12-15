// API utilities for communicating with Python backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const DEFAULT_TIMEOUT_MS = 30000; // 30 seconds

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {},
  timeoutMs: number = DEFAULT_TIMEOUT_MS
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Create AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for auth
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}`);
    }

    return response.json();
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Request timed out. Please try again.');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ============================================
// Projects API
// ============================================

export interface ProjectResponse {
  success: boolean;
  project?: Project;
  projects?: Project[];
  count?: number;
  message?: string;
}

export interface Project {
  project_id: string;
  user_id?: string;
  project_name: string;
  wordpress_url: string;
  wordpress_username: string;
  wordpress_app_password: string;
  html_configs: HtmlConfigs | null;
  image_configs: ImageConfigs | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  last_published_at: string | null;
}

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

export interface HtmlPattern {
  element_type: string;
  source_pattern: string;
  target_pattern: string;
}

export interface HtmlConfigs {
  patterns: HtmlPattern[];
}

export interface ProjectCreateData {
  project_id: string;
  project_name: string;
  wordpress_url: string;
  wordpress_username: string;
  wordpress_app_password: string;
  html_configs?: HtmlConfigs | null;
  image_configs?: ImageConfigs | null;
  notes?: string;
  user_id?: string;
}

export interface ProjectUpdateData {
  project_name?: string;
  wordpress_url?: string;
  wordpress_username?: string;
  wordpress_app_password?: string;
  html_configs?: HtmlConfigs | null;
  image_configs?: ImageConfigs | null;
  notes?: string;
  status?: string;
}

export async function getProjects(status: string = 'all', userId?: string): Promise<ProjectResponse> {
  const params = new URLSearchParams({ status });
  if (userId) {
    params.append('user_id', userId);
  }
  return fetchApi<ProjectResponse>(`/api/projects/?${params}`);
}

export async function getProject(projectId: string, userId?: string): Promise<ProjectResponse> {
  const params = userId ? `?user_id=${userId}` : '';
  return fetchApi<ProjectResponse>(`/api/projects/${projectId}${params}`);
}

export async function createProject(data: ProjectCreateData): Promise<ProjectResponse> {
  return fetchApi<ProjectResponse>('/api/projects/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateProject(
  projectId: string,
  data: ProjectUpdateData,
  userId?: string
): Promise<ProjectResponse> {
  const params = userId ? `?user_id=${userId}` : '';
  return fetchApi<ProjectResponse>(`/api/projects/${projectId}${params}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteProject(projectId: string, userId?: string): Promise<ProjectResponse> {
  const params = userId ? `?user_id=${userId}` : '';
  return fetchApi<ProjectResponse>(`/api/projects/${projectId}${params}`, {
    method: 'DELETE',
  });
}

// ============================================
// Publishing API
// ============================================

export interface PublishRequest {
  google_docs_url: string;
  project_id?: string;
  main_keyword?: string;
}

export interface PublishResponse {
  success: boolean;
  post_id?: number;
  post_url?: string;
  edit_url?: string;
  post_title?: string;
  post_status?: string;
  images_processed?: number;
  execution_time?: number;
  error?: string;
  step_failed?: string;
}

export async function publishSingle(data: PublishRequest): Promise<PublishResponse> {
  // Publishing can take 1-2 minutes, so use longer timeout
  return fetchApi<PublishResponse>('/api/publish/single', {
    method: 'POST',
    body: JSON.stringify(data),
  }, 120000); // 2 minutes
}

export interface BatchItem {
  url: string;
  keyword?: string;
}

export interface BatchPublishRequest {
  project_id: string;
  items: BatchItem[];
}

export interface BatchItemResult {
  url: string;
  success: boolean;
  post_url?: string;
  post_title?: string;
  error?: string;
}

export interface BatchPublishResponse {
  success: boolean;
  total: number;
  completed: number;
  failed: number;
  results: BatchItemResult[];
}

export async function publishBatch(data: BatchPublishRequest): Promise<BatchPublishResponse> {
  // Batch publishing can take a long time, use extended timeout
  return fetchApi<BatchPublishResponse>('/api/publish/batch', {
    method: 'POST',
    body: JSON.stringify(data),
  }, 600000); // 10 minutes
}

// ============================================
// History API
// ============================================

export interface HistoryEntry {
  id: number;
  project_id: string | null;
  project_name: string | null;
  google_docs_url: string;
  wordpress_post_id: number | null;
  wordpress_post_url: string | null;
  post_title: string | null;
  post_status: string | null;
  images_processed: number;
  success: boolean;
  error_message: string | null;
  execution_time_seconds: number | null;
  published_at: string;
}

export interface HistoryResponse {
  success: boolean;
  history: HistoryEntry[];
  count: number;
}

export async function getHistory(
  projectId?: string,
  limit: number = 50
): Promise<HistoryResponse> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (projectId) {
    params.append('project_id', projectId);
  }
  return fetchApi<HistoryResponse>(`/api/history/?${params}`);
}

export async function getFailedPublishes(limit: number = 20): Promise<HistoryResponse> {
  return fetchApi<HistoryResponse>(`/api/history/failed?limit=${limit}`);
}

export interface HistoryStatsResponse {
  success: boolean;
  total: number;
  successful: number;
  failed: number;
  success_rate: number;
}

export async function getHistoryStats(projectId?: string): Promise<HistoryStatsResponse> {
  const params = projectId ? `?project_id=${projectId}` : '';
  return fetchApi<HistoryStatsResponse>(`/api/history/stats${params}`);
}

// ============================================
// Patterns API
// ============================================

// Constants matching backend validation
const MAX_INSTRUCTION_LENGTH = 500;
const MAX_HTML_CONTENT_LENGTH = 100000;

export interface ScanPatternResponse {
  success: boolean;
  patterns?: HtmlPattern[];
  elements_found?: string[];
  notes?: string;
  error?: string;
}

export interface ModifyPatternResponse {
  success: boolean;
  patterns?: HtmlPattern[];
  changes_made?: string;
  error?: string;
}

export async function scanHtmlForPatterns(
  htmlContent: string
): Promise<ScanPatternResponse> {
  // Client-side validation
  if (!htmlContent || htmlContent.trim().length < 10) {
    return {
      success: false,
      error: 'HTML content must be at least 10 characters',
    };
  }
  if (htmlContent.length > MAX_HTML_CONTENT_LENGTH) {
    return {
      success: false,
      error: `HTML content exceeds maximum length (${MAX_HTML_CONTENT_LENGTH / 1000}KB)`,
    };
  }

  return fetchApi<ScanPatternResponse>('/api/patterns/scan', {
    method: 'POST',
    body: JSON.stringify({ html_content: htmlContent }),
  }, 90000); // 90 second timeout for AI processing
}

export async function modifyPatterns(
  currentPatterns: HtmlPattern[],
  instruction: string
): Promise<ModifyPatternResponse> {
  // Client-side validation
  if (!instruction || instruction.trim().length < 3) {
    return {
      success: false,
      error: 'Instruction must be at least 3 characters',
    };
  }
  if (instruction.length > MAX_INSTRUCTION_LENGTH) {
    return {
      success: false,
      error: `Instruction must be ${MAX_INSTRUCTION_LENGTH} characters or less`,
    };
  }

  return fetchApi<ModifyPatternResponse>('/api/patterns/modify', {
    method: 'POST',
    body: JSON.stringify({
      current_patterns: currentPatterns,
      instruction: instruction,
    }),
  }, 90000); // 90 second timeout for AI processing
}
