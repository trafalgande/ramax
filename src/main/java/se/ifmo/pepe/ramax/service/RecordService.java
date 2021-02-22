package se.ifmo.pepe.ramax.service;

import org.apache.commons.exec.CommandLine;
import org.apache.commons.exec.DefaultExecutor;
import org.apache.commons.exec.PumpStreamHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import se.ifmo.pepe.ramax.model.CustomRecord;
import se.ifmo.pepe.ramax.model.OptimisationData;
import se.ifmo.pepe.ramax.repository.RecordRepository;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

@Service
public class RecordService {
    final RecordRepository recordRepository;

    @Autowired
    public RecordService(RecordRepository recordRepository) {
        this.recordRepository = recordRepository;
    }

    public void openFile(String PATH) throws IOException {
        List<String> lines = Files.readAllLines(Path.of(PATH), Charset.forName("Windows-1251"));
        recordRepository.deleteAllInBatch();
        for (int i = 1; i < lines.size(); i++) {
            String[] current = lines.get(i).split("\"");
            recordRepository.save(new CustomRecord()
                    .setDate(current[0].split(",")[0])
                    .setWeekDay(current[0].split(",")[1])
                    .setMerch(current[0].split(",")[2])
                    .setTTOrder(current[0].split(",")[3])
                    .setTTName(current[0].split(",")[4])
                    .setTTAddress(current[1])
                    .setArrivalTime(current[2].split(",")[1])
                    .setDurationTime(current[2].split(",")[2])
                    .setFrequencyPerWeek(current[2].split(",")[3])
                    .setDistanceForNext(current[2].split(",")[4])
            );
        }

    }

    public HashMap<String, List<String>> fetchMerch(String merch) {
        ArrayList<CustomRecord> merchList = recordRepository.findAllByMerch(merch);
        HashMap<String, List<String>> traverseCalendar = new HashMap<>();

        ArrayList<String> buff = new ArrayList<>();

        for (CustomRecord c : merchList) {
            if (!traverseCalendar.containsKey(c.getWeekDay())) {
                buff = new ArrayList<>();
                traverseCalendar.put(c.getWeekDay(), buff);
            }
            buff.add(c.getTTAddress());
        }

        return traverseCalendar;
    }

    public TreeSet<String> fetchAllUniqueMerchandisers(String PATH) throws IOException {
        openFile(PATH);
        TreeSet<String> set = new TreeSet<>();
        for (CustomRecord c : recordRepository.findAll()) {
            set.add(c.getMerch());
        }
        return set;
    }

    public OptimisationData fetchOptimisationReportData(String REPORT_PATH) throws IOException {
        List<String> lines = Files.readAllLines(Path.of(REPORT_PATH), Charset.forName("Windows-1251"));

        return new OptimisationData()
                .setTTAmount__pctChange(Double.valueOf(lines.get(1).split(",")[4]))
                .setMerchAmount__pctChange(Double.valueOf(lines.get(2).split(",")[4]))
                .setAvgRoute__pctChange(Double.valueOf(lines.get(3).split(",")[5]))
                .setAvgWorkingHours__pctChange(Double.valueOf(lines.get(5).split(",")[4]));
    }

    public List<String> findTraverseOnParticularWeekDay(String merch, String weekDay) {
        HashMap<String, List<String>> map = fetchMerch(merch);
        System.out.println(weekDay);
        return map.get(weekDay);
    }

    public Set<String> findWeekDaysForParticularMerchandiser(String merch) {
        HashMap<String, List<String>> map = fetchMerch(merch);
        return map.keySet();
    }

    public void resolve() throws IOException {
        cmd("python script_maximization.py input_matrix.csv input_origin.csv input_plan.csv out/out_report.csv out/out_data.csv");
        fetchAllUniqueMerchandisers("python/out/out_data.csv");
    }

    private String cmd(String command) throws IOException {
        CommandLine cmdLine = CommandLine.parse(command);
        ByteArrayOutputStream stdout = new ByteArrayOutputStream();
        ByteArrayOutputStream stderr = new ByteArrayOutputStream();
        PumpStreamHandler streamHandler = new PumpStreamHandler(stdout, stderr);
        DefaultExecutor executor = new DefaultExecutor();
        executor.setWorkingDirectory(new File("python/"));
        executor.setStreamHandler(streamHandler);
        executor.execute(cmdLine);
        return stdout.toString();
    }
}
