"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { CreditCard, MapPin, Info } from "lucide-react";

interface OrganizationData {
  name: string;
  billing_email?: string;
  billing_address?: string;
  timezone: string;
}

interface BillingInfoStepProps {
  data: OrganizationData;
  onDataChange: (data: Partial<OrganizationData>) => void;
  isLoading: boolean;
}

export default function BillingInfoStep({
  data,
  onDataChange,
  isLoading,
}: BillingInfoStepProps) {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [skipBilling, setSkipBilling] = useState(false);

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const handleInputChange = (field: string, value: string) => {
    onDataChange({ [field]: value });
    
    const newErrors = { ...errors };
    
    if (field === "billing_email" && value) {
      if (!validateEmail(value)) {
        newErrors.billing_email = "Please enter a valid email address";
      } else {
        delete newErrors.billing_email;
      }
    }
    
    if (field === "billing_address" && value && value.length > 500) {
      newErrors.billing_address = "Address must be less than 500 characters";
    } else if (field === "billing_address") {
      delete newErrors.billing_address;
    }
    
    setErrors(newErrors);
  };

  const handleSkipBillingChange = (checked: boolean) => {
    setSkipBilling(checked);
    if (checked) {
      onDataChange({ billing_email: "", billing_address: "" });
      setErrors({});
    }
  };

  return (
    <div className="space-y-6">
      {/* Skip Billing Option */}
      <div className="flex items-center space-x-2">
        <Checkbox
          id="skip-billing"
          checked={skipBilling}
          onCheckedChange={handleSkipBillingChange}
          disabled={isLoading}
        />
        <Label htmlFor="skip-billing" className="text-sm">
          Skip billing setup for now (you can add this later)
        </Label>
      </div>

      {!skipBilling && (
        <>
          {/* Billing Email */}
          <div className="space-y-2">
            <Label htmlFor="billing_email" className="flex items-center space-x-2">
              <CreditCard className="w-4 h-4" />
              <span>Billing Email</span>
            </Label>
            <Input
              id="billing_email"
              type="email"
              placeholder="billing@yourcompany.com"
              value={data.billing_email || ""}
              onChange={(e) => handleInputChange("billing_email", e.target.value)}
              className={errors.billing_email ? "border-red-500" : ""}
              disabled={isLoading}
            />
            {errors.billing_email && (
              <p className="text-sm text-red-600">{errors.billing_email}</p>
            )}
            <p className="text-sm text-gray-500">
              We&apos;ll send invoices and billing notifications to this email
            </p>
          </div>

          {/* Billing Address */}
          <div className="space-y-2">
            <Label htmlFor="billing_address" className="flex items-center space-x-2">
              <MapPin className="w-4 h-4" />
              <span>Billing Address</span>
            </Label>
            <Textarea
              id="billing_address"
              placeholder="Enter your complete billing address..."
              value={data.billing_address || ""}
              onChange={(e) => handleInputChange("billing_address", e.target.value)}
              className={errors.billing_address ? "border-red-500" : ""}
              rows={3}
              disabled={isLoading}
            />
            {errors.billing_address && (
              <p className="text-sm text-red-600">{errors.billing_address}</p>
            )}
            <p className="text-sm text-gray-500">
              Include street address, city, state/province, and postal code
            </p>
          </div>
        </>
      )}

      {/* Info Card */}
      <Card className="bg-green-50 border-green-200">
        <CardContent className="pt-4">
          <div className="flex items-start space-x-3">
            <Info className="w-5 h-5 text-green-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-green-900 mb-1">
                Billing Information
              </h4>
              <p className="text-sm text-green-700 mb-2">
                {skipBilling 
                  ? "You can add billing information later in your organization settings. This won&apos;t affect your ability to create events and forms."
                  : "This information will be used for invoicing and billing purposes. You can update it anytime in your organization settings."
                }
              </p>
              {!skipBilling && (
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• Secure storage with encryption</li>
                  <li>• Easy to update later</li>
                  <li>• Used for tax and compliance purposes</li>
                </ul>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validation Summary */}
      {Object.keys(errors).length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-800">
            Please fix the errors above before continuing
          </p>
        </div>
      )}
    </div>
  );
}
