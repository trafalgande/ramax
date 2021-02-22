package se.ifmo.pepe.ramax.model;

import lombok.Data;

import java.io.Serializable;
import java.text.DecimalFormat;

@Data
public class OptimisationData implements Serializable {
    public Double TTAmount__pctChange = 0.d;
    public Double MerchAmount__pctChange = 0.d;
    public Double AvgRoute__pctChange = 0.d;
    public Double AvgWorkingHours__pctChange = 0.d;
    private DecimalFormat df = new DecimalFormat("#.#### %");

    public String getTTAmount__pctChange() {
        return df.format(-(TTAmount__pctChange / 100) );
    }

    public String getMerchAmount__pctChange() {
        return df.format(-(MerchAmount__pctChange / 100) );
    }

    public String getAvgRoute__pctChange() {
        return df.format(-(AvgRoute__pctChange / 100));
    }

    public String getAvgWorkingHours__pctChange() {
        return df.format(-AvgWorkingHours__pctChange / 100);
    }

    public OptimisationData setTTAmount__pctChange(Double TTAmount__pctChange) {
        TTAmount__pctChange = TTAmount__pctChange;
        return this;
    }

    public OptimisationData setMerchAmount__pctChange(Double merchAmount__pctChange) {
        MerchAmount__pctChange = merchAmount__pctChange;
        return this;
    }

    public OptimisationData setAvgRoute__pctChange(Double avgRoute__pctChange) {
        AvgRoute__pctChange = avgRoute__pctChange;
        return this;
    }

    public OptimisationData setAvgWorkingHours__pctChange(Double avgWorkingHours__pctChange) {
        AvgWorkingHours__pctChange = avgWorkingHours__pctChange;
        return this;
    }
}
