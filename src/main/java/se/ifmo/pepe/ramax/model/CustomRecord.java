package se.ifmo.pepe.ramax.model;


import lombok.Data;
import org.springframework.format.datetime.DateFormatter;

import javax.persistence.*;
import java.io.Serializable;
import java.text.ParseException;
import java.util.Comparator;
import java.util.Date;
import java.util.Locale;
import java.util.Objects;

@Data
@Entity
@Table(name = "records")
public class CustomRecord implements Serializable {

    @Id
    @Column(name = "id")
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long ID;

    @Column(name = "date")
    private Date date = null;

    @Column(name = "weekDay")
    private String weekDay = null;

    @Column(name = "merch")
    private String merch = null;

    @Column(name = "TT_Order")
    private String TTOrder = null;

    @Column(name = "TT_Name")
    private String TTName = null;

    @Column(name = "TT_Address")
    private String TTAddress = null;

    @Column(name = "arrivalTime")
    private String arrivalTime = null;

    @Column(name = "durationTime")
    private String durationTime = null;

    @Column(name = "frequencyPerWeek")
    private String frequencyPerWeek = null;

    @Column(name = "distanceForNext")
    private String distanceForNext = null;

    public CustomRecord setDate(String date) {
        DateFormatter dateFormatter = new DateFormatter("dd.MM.yyyy");

        try {
            this.date = dateFormatter.parse(date, Locale.ROOT);
        } catch (ParseException e) {
            e.printStackTrace();
        }
        return this;
    }
    public CustomRecord setWeekDay(String weekDay) {
        this.weekDay = weekDay;
        return this;
    }
    public CustomRecord setMerch(String merch) {
        this.merch = merch;
        return this;
    }
    public CustomRecord setTTOrder(String TTOrder) {
        this.TTOrder = TTOrder;
        return this;
    }
    public CustomRecord setTTName(String TTName) {
        this.TTName = TTName;
        return this;
    }
    public CustomRecord setTTAddress(String TTAddress) {
        this.TTAddress = TTAddress;
        return this;
    }
    public CustomRecord setArrivalTime(String arrivalTime) {
        this.arrivalTime = arrivalTime;
        return this;
    }
    public CustomRecord setDurationTime(String durationTime) {
        this.durationTime = durationTime;
        return this;
    }
    public CustomRecord setFrequencyPerWeek(String frequencyPerWeek) {
        this.frequencyPerWeek = frequencyPerWeek;
        return this;
    }
    public CustomRecord setDistanceForNext(String distanceForNext) {
        this.distanceForNext = distanceForNext;
        return this;
    }


}
