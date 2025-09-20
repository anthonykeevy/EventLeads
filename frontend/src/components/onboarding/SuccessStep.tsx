"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Building2, Users, Calendar, ArrowRight } from "lucide-react";

interface OrganizationData {
  name: string;
  billing_email?: string;
  billing_address?: string;
  timezone: string;
}

interface SuccessStepProps {
  data: OrganizationData;
  onDataChange: (data: Partial<OrganizationData>) => void;
  isLoading: boolean;
  createdOrganization: any;
  onComplete: () => void;
}

export default function SuccessStep({
  data,
  createdOrganization,
  onComplete,
}: SuccessStepProps) {
  return (
    <div className="space-y-6">
      {/* Success Message */}
      <div className="text-center space-y-4">
        <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            Welcome to {data.name}!
          </h3>
          <p className="text-gray-600">
            Your organization has been created successfully. You&apos;re now an Admin and can start building amazing event forms.
          </p>
        </div>
      </div>

      {/* Organization Card */}
      <Card className="border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Building2 className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">{data.name}</h4>
                <p className="text-sm text-gray-600">Organization ID: {createdOrganization?.id}</p>
              </div>
            </div>
            <Badge variant="secondary" className="bg-green-100 text-green-800">
              Active
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-3 bg-white rounded-lg">
              <Users className="w-5 h-5 text-blue-600 mx-auto mb-1" />
              <p className="text-sm text-gray-600">Max Users</p>
              <p className="font-semibold text-gray-900">5</p>
            </div>
            <div className="text-center p-3 bg-white rounded-lg">
              <Calendar className="w-5 h-5 text-blue-600 mx-auto mb-1" />
              <p className="text-sm text-gray-600">Max Events</p>
              <p className="font-semibold text-gray-900">10</p>
            </div>
            <div className="text-center p-3 bg-white rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600 mx-auto mb-1" />
              <p className="text-sm text-gray-600">Plan</p>
              <p className="font-semibold text-gray-900">Basic</p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-green-200">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>Timezone: {data.timezone}</span>
              <span>Created: {new Date().toLocaleDateString()}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Next Steps */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <h4 className="font-semibold text-blue-900 mb-3">What&apos;s next?</h4>
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                1
              </div>
              <span className="text-blue-800">Explore your dashboard and organization settings</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                2
              </div>
              <span className="text-blue-800">Invite team members to collaborate</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                3
              </div>
              <span className="text-blue-800">Create your first event and form</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Button */}
      <div className="text-center pt-4">
        <Button 
          onClick={onComplete}
          size="lg"
          className="bg-blue-600 hover:bg-blue-700 text-white px-8"
        >
          Go to Dashboard
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-sm text-gray-500">
          Need help getting started?{" "}
          <button className="text-blue-600 hover:text-blue-700 underline">
            View our getting started guide
          </button>
        </p>
      </div>
    </div>
  );
}
