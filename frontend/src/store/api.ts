import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

// Define types for our API responses
export interface Employee {
  id: string;
  name: string;
  email: string;
  designation: string;
  is_active: boolean;
  onboarded_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  project_type: string;
  duration_months: number;
  tech_stack: string[];
  required_skills: string[];
}

export interface Allocation {
  id: string;
  project_id: string;
  employee_id: string;
  percent_allocated: string;
  start_date: string;
  end_date: string;
  status: string;
}

export interface CreateAllocationRequest {
  project_id: string;
  employee_id: string;
  percent_allocated: string;
  start_date: string;
  end_date: string;
}

// Define the API slice
export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1',
    prepareHeaders: headers => {
      // Add auth headers if needed
      headers.set('Content-Type', 'application/json');
      return headers;
    },
  }),
  tagTypes: ['Employee', 'Project', 'Allocation'],
  endpoints: builder => ({
    // Employee endpoints
    getEmployees: builder.query<Employee[], void>({
      query: () => '/employees',
      providesTags: ['Employee'],
    }),
    getEmployee: builder.query<Employee, string>({
      query: id => `/employees/${id}`,
      providesTags: ['Employee'],
    }),

    // Project endpoints
    getProjects: builder.query<Project[], void>({
      query: () => '/projects',
      providesTags: ['Project'],
    }),
    getProject: builder.query<Project, string>({
      query: id => `/projects/${id}`,
      providesTags: ['Project'],
    }),

    // Allocation endpoints
    getAllocations: builder.query<Allocation[], void>({
      query: () => '/allocations',
      providesTags: ['Allocation'],
    }),
    createAllocation: builder.mutation<Allocation, CreateAllocationRequest>({
      query: allocation => ({
        url: '/allocations',
        method: 'POST',
        body: allocation,
      }),
      invalidatesTags: ['Allocation'],
    }),
    updateAllocation: builder.mutation<
      Allocation,
      { id: string; allocation: Partial<CreateAllocationRequest> }
    >({
      query: ({ id, allocation }) => ({
        url: `/allocations/${id}`,
        method: 'PUT',
        body: allocation,
      }),
      invalidatesTags: ['Allocation'],
    }),
    deleteAllocation: builder.mutation<void, string>({
      query: id => ({
        url: `/allocations/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Allocation'],
    }),

    // Health check
    getHealth: builder.query<{ status: string; timestamp: string }, void>({
      query: () => '/health',
    }),
  }),
});

// Export hooks for usage in functional components
export const {
  useGetEmployeesQuery,
  useGetEmployeeQuery,
  useGetProjectsQuery,
  useGetProjectQuery,
  useGetAllocationsQuery,
  useCreateAllocationMutation,
  useUpdateAllocationMutation,
  useDeleteAllocationMutation,
  useGetHealthQuery,
} = api;
