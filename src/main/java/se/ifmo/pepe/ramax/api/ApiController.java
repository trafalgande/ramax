package se.ifmo.pepe.ramax.api;


import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.ModelAndView;
import se.ifmo.pepe.ramax.service.RecordService;
import se.ifmo.pepe.ramax.utils.ZipUtil;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.text.ParseException;
import java.util.List;
import java.util.Set;

@RestController
@RequestMapping("/api")
public class ApiController {
    private final RecordService recordService;

    @Value("${map.api.key}")
    String API_KEY;

    @Autowired
    public ApiController(RecordService recordService) {
        this.recordService = recordService;
    }


    @RequestMapping("/week")
    public Set<String> fetchWeekDays(@RequestParam(name = "merch", required = false) String merch) {
        return recordService.findWeekDaysForParticularMerchandiser(merch);
    }

    @RequestMapping("/find")
    public String find(@RequestParam(name = "merch", required = false) String merch,
                       @RequestParam(name = "weekDay", required = false) String weekDay) throws ParseException {

        List<String> list = recordService.findTraverseOnParticularWeekDay(merch, weekDay);
        String value = String.format("https://www.google.com/maps/embed/v1/directions" +
                        "?key=%s" +
                        "&origin=%s" +
                        "&destination=%s",
                API_KEY, list.get(0), list.get(list.size() - 1));

        if (list.size() > 2) {
            StringBuilder sb = new StringBuilder();
            for (int i = 1; i < list.size() - 1; i++) {
                if (i == 1)
                    sb.append(list.get(i));
                else
                    sb.append("|").append(list.get(i));
            }
            value += String.format("&waypoints=%s", sb);
        }
        return value;
    }


    @RequestMapping("/process")
    public ModelAndView process(@RequestParam(name = "files", required = false) MultipartFile[] files) throws IOException {
        for (MultipartFile f : files) {
            Files.deleteIfExists(Paths.get("python/" + f.getOriginalFilename()));
            Files.copy(f.getInputStream(), Paths.get("python/" + f.getOriginalFilename()));
        }
        ModelAndView model = new ModelAndView();
        recordService.resolve();
        model.addObject("options", recordService.fetchAllUniqueMerchandisers("python/out/out_data.csv"));
        model.addObject("stats", recordService.fetchOptimisationReportData("python/out/out_report.csv"));
        model.setViewName("/index.html");
        return model;
    }

    @GetMapping(
            value = {"/download"},
            produces = {"application/zip"}
    )
    public ResponseEntity<FileSystemResource> downloadZip() throws Exception {
        Files.deleteIfExists(Path.of("python/report.zip"));
        ZipUtil.zipFolder(Path.of("python/out"), Path.of("python/report.zip"));
        File file = new File("python/report.zip");
        return
                ResponseEntity.ok()
                        .contentType(MediaType.parseMediaType("application/zip"))
                        .contentLength(file.length())
                        .header("Content-Disposition", new String[]{"attachment; charset=windows-1251; filename=\"report.zip\""}).body(new FileSystemResource(file));
    }
}
