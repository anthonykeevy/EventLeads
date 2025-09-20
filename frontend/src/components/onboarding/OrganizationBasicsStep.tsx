"use client";

import { useState, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Building2, Globe, Clock } from "lucide-react";
import { useOnboardingAnalytics } from "@/lib/analytics";

interface OrganizationData {
  name: string;
  billing_email?: string;
  billing_address?: string;
  timezone: string;
}

interface OrganizationBasicsStepProps {
  data: OrganizationData;
  onDataChange: (data: Partial<OrganizationData>) => void;
  isLoading: boolean;
}

const timezones = [
  { value: "UTC", label: "UTC (Coordinated Universal Time)" },
  { value: "America/New_York", label: "Eastern Time (ET)" },
  { value: "America/Chicago", label: "Central Time (CT)" },
  { value: "America/Denver", label: "Mountain Time (MT)" },
  { value: "America/Los_Angeles", label: "Pacific Time (PT)" },
  { value: "Europe/London", label: "London (GMT/BST)" },
  { value: "Europe/Paris", label: "Paris (CET/CEST)" },
  { value: "Asia/Tokyo", label: "Tokyo (JST)" },
  { value: "Asia/Shanghai", label: "Shanghai (CST)" },
  { value: "Australia/Sydney", label: "Sydney (AEST/AEDT)" },
];

export default function OrganizationBasicsStep({
  data,
  onDataChange,
  isLoading,
}: OrganizationBasicsStepProps) {
  const analytics = useOnboardingAnalytics();
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateField = (field: string, value: string) => {
    const newErrors = { ...errors };
    
    switch (field) {
      case "name":
        if (!value.trim()) {
          newErrors.name = "Organization name is required";
          analytics.trackValidationError("name", "Organization name is required");
        } else if (value.trim().length < 2) {
          newErrors.name = "Organization name must be at least 2 characters";
          analytics.trackValidationError("name", "Organization name must be at least 2 characters");
        } else if (value.trim().length > 255) {
          newErrors.name = "Organization name must be less than 255 characters";
          analytics.trackValidationError("name", "Organization name must be less than 255 characters");
        } else {
          delete newErrors.name;
        }
        break;
      case "timezone":
        if (!value) {
          newErrors.timezone = "Timezone is required";
          analytics.trackValidationError("timezone", "Timezone is required");
        } else {
          delete newErrors.timezone;
        }
        break;
    }
    
    setErrors(newErrors);
  };

  const handleInputChange = (field: string, value: string) => {
    onDataChange({ [field]: value });
    validateField(field, value);
  };

  const handleFieldFocus = (fieldName: string) => {
    analytics.trackFieldInteraction(fieldName, 'focused');
  };

  const handleFieldBlur = (fieldName: string) => {
    analytics.trackFieldInteraction(fieldName, 'blurred');
  };

  const isValid = !errors.name && !errors.timezone && data.name.trim().length > 0;

  return (
    <div className="space-y-6">
      {/* Organization Name */}
      <div className="space-y-2">
        <Label htmlFor="name" className="flex items-center space-x-2">
          <Building2 className="w-4 h-4" />
          <span>Organization Name *</span>
        </Label>
        <Input
          id="name"
          type="text"
          placeholder="Enter your organization name"
          value={data.name}
          onChange={(e) => handleInputChange("name", e.target.value)}
          onFocus={() => handleFieldFocus("name")}
          onBlur={() => handleFieldBlur("name")}
          className={errors.name ? "border-red-500" : ""}
          disabled={isLoading}
        />
        {errors.name && (
          <p className="text-sm text-red-600">{errors.name}</p>
        )}
        <p className="text-sm text-gray-500">
          This will be displayed on your forms and dashboard
        </p>
      </div>

      {/* Timezone */}
      <div className="space-y-2">
        <Label htmlFor="timezone" className="flex items-center space-x-2">
          <Clock className="w-4 h-4" />
          <span>Timezone *</span>
        </Label>
        <Select
          value={data.timezone}
          onValueChange={(value) => handleInputChange("timezone", value)}
          onOpenChange={(open) => {
            if (open) {
              analytics.trackFieldInteraction("timezone", 'focused');
            } else {
              analytics.trackFieldInteraction("timezone", 'blurred');
            }
          }}
          disabled={isLoading}
        >
          <SelectTrigger className={errors.timezone ? "border-red-500" : ""}>
            <SelectValue placeholder="Select your timezone" />
          </SelectTrigger>
          <SelectContent>
            {timezones.map((tz) => (
              <SelectItem key={tz.value} value={tz.value}>
                {tz.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {errors.timezone && (
          <p className="text-sm text-red-600">{errors.timezone}</p>
        )}
        <p className="text-sm text-gray-500">
          This will be used for scheduling and time-based features
        </p>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-4">
          <div className="flex items-start space-x-3">
            <Globe className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900 mb-1">
                What happens next?
              </h4>
              <p className="text-sm text-blue-700">
                After creating your organization, you&apos;ll be automatically assigned as an Admin. 
                You can then invite team members and start creating your first event forms.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validation Summary */}
      {!isValid && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
          <p className="text-sm text-yellow-800">
            Please fill in all required fields to continue
          </p>
        </div>
      )}
    </div>
  );
}
