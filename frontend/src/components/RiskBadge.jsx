import React from 'react';
import { Shield, AlertTriangle, AlertCircle, XOctagon } from 'lucide-react';

const RiskBadge = ({ level = 'low', size = 'md' }) => {
  const config = {
    low: {
      bgColor: 'bg-green-100',
      textColor: 'text-green-800',
      borderColor: 'border-green-200',
      icon: Shield,
      label: 'Low Risk',
    },
    medium: {
      bgColor: 'bg-yellow-100',
      textColor: 'text-yellow-800',
      borderColor: 'border-yellow-200',
      icon: AlertCircle,
      label: 'Medium Risk',
    },
    high: {
      bgColor: 'bg-orange-100',
      textColor: 'text-orange-800',
      borderColor: 'border-orange-200',
      icon: AlertTriangle,
      label: 'High Risk',
    },
    critical: {
      bgColor: 'bg-red-100',
      textColor: 'text-red-800',
      borderColor: 'border-red-200',
      icon: XOctagon,
      label: 'Critical Risk',
    },
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  const iconSizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };

  const currentConfig = config[level] || config.low;
  const Icon = currentConfig.icon;

  return (
    <div
      className={`inline-flex items-center space-x-1 rounded-full border ${currentConfig.bgColor} ${currentConfig.borderColor} ${currentConfig.textColor} ${sizeClasses[size]}`}
    >
      <Icon className={iconSizes[size]} />
      <span className="font-medium">{currentConfig.label}</span>
    </div>
  );
};

export default RiskBadge;
