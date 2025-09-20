"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, ArrowRight, CheckCircle } from "lucide-react";
import { useOnboardingAnalytics } from "@/lib/analytics";
import { getToken } from "@/lib/auth";

// Step Components
import OrganizationBasicsStep from "@/components/onboarding/OrganizationBasicsStep";
import BillingInfoStep from "@/components/onboarding/BillingInfoStep";
import SuccessStep from "@/components/onboarding/SuccessStep";

// Types
interface OrganizationData {
  name: string;
  billing_email?: string;
  billing_address?: string;
  timezone: string;
}

interface WizardStep {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<any>;
}

const steps: WizardStep[] = [
  {
    id: "organization_basics",
    title: "Organization Details",
    description: "Tell us about your organization",
    component: OrganizationBasicsStep,
  },
  {
    id: "billing_info",
    title: "Billing Information",
    description: "Set up billing details (optional)",
    component: BillingInfoStep,
  },
  {
    id: "success",
    title: "Welcome!",
    description: "Your organization is ready",
    component: SuccessStep,
  },
];

export default function OnboardingPage() {
  const router = useRouter();
  const analytics = useOnboardingAnalytics();
  const [currentStep, setCurrentStep] = useState(0);
  const [organizationData, setOrganizationData] = useState<OrganizationData>({
    name: "",
    timezone: "UTC",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [createdOrganization, setCreatedOrganization] = useState<any>(null);

  const progress = ((currentStep + 1) / steps.length) * 100;

  // Track step changes
  useEffect(() => {
    const currentStepData = steps[currentStep];
    analytics.trackStepStarted(currentStepData.id);
    
    return () => {
      // Track step completion when component unmounts or step changes
      analytics.trackStepCompleted(currentStepData.id);
    };
  }, [currentStep, analytics]);

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      analytics.trackButtonClick('next', steps[currentStep].id);
      setCurrentStep(currentStep + 1);
      setError(null);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      analytics.trackButtonClick('previous', steps[currentStep].id);
      setCurrentStep(currentStep - 1);
      setError(null);
    }
  };

  const handleDataChange = (stepData: Partial<OrganizationData>) => {
    setOrganizationData((prev) => ({ ...prev, ...stepData }));
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const token = getToken();
      if (!token) {
        setIsLoading(false);
        setError("You are not signed in. Please log in and try again.");
        router.push("/login");
        return;
      }

      const response = await fetch("/organizations", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(organizationData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        try {
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.detail || "Failed to create organisation");
        } catch {
          throw new Error(errorText?.slice(0, 160) || "Failed to create organisation");
        }
      }

      const result = await response.json();
      setCreatedOrganization(result);
      
      analytics.trackWizardCompleted(organizationData);
      
      setCurrentStep(steps.length - 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
      analytics.trackValidationError('organization_creation', err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplete = () => {
    analytics.trackButtonClick('go_to_dashboard', 'success');
    router.push("/dashboard");
  };

  const CurrentStepComponent = steps[currentStep].component;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome to EventLeads
          </h1>
          <p className="text-gray-600">
            Let&apos;s set up your organisation in just a few steps
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Step {currentStep + 1} of {steps.length}</span>
            <span>{Math.round(progress)}% Complete</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Step Indicator */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-4">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`flex items-center space-x-2 ${
                  index <= currentStep ? "text-blue-600" : "text-gray-400"
                }`}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    index < currentStep
                      ? "bg-blue-600 text-white"
                      : index === currentStep
                      ? "bg-blue-100 text-blue-600 border-2 border-blue-600"
                      : "bg-gray-200 text-gray-400"
                  }`}
                >
                  {index < currentStep ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    index + 1
                  )}
                </div>
                <span className="hidden sm:block text-sm font-medium">
                  {step.title}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl text-center">
              {steps[currentStep].title}
            </CardTitle>
            <p className="text-center text-gray-600">
              {steps[currentStep].description}
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Step Content */}
            <CurrentStepComponent
              data={organizationData}
              onDataChange={handleDataChange}
              isLoading={isLoading}
              createdOrganization={createdOrganization}
              onComplete={handleComplete}
            />

            {/* Navigation */}
            {currentStep < steps.length - 1 && (
              <div className="flex justify-between pt-6 border-t">
                <Button
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={currentStep === 0}
                  className="flex items-center space-x-2"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Previous</span>
                </Button>

                <Button
                  onClick={
                    currentStep === steps.length - 2
                      ? handleSubmit
                      : handleNext
                  }
                  disabled={isLoading}
                  className="flex items-center space-x-2"
                >
                  <span>
                    {currentStep === steps.length - 2 ? "Create Organisation" : "Next"}
                  </span>
                  {currentStep < steps.length - 2 && <ArrowRight className="w-4 h-4" />}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Help Text */}
        <div className="text-center mt-6">
          <p className="text-sm text-gray-500">
            Need help?{" "}
            <button className="text-blue-600 hover:text-blue-700 underline">
              Contact support
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}
